from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseNotAllowed, JsonResponse
from django.core.mail import send_mail, BadHeaderError
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import csv

import io
import xlsxwriter
from reportlab.pdfgen import canvas
from django.http import FileResponse, HttpResponse
from django.db.models import Avg



from .models import Pago, Usuario, Cabana, Reserva, Comentario, Inventario
from app import models
from .forms import CabanaForm




# Página principal
def index(request):
    cabanas_disponibles = Cabana.objects.filter(estado='Disponible')
    return render(request, 'index.html', {
        'cabanas_disponibles': cabanas_disponibles,
        'nombre': request.session.get('usuario_nombre', '')
    })

# Login
def login_view(request):
    mensaje = ''
    if request.method == 'POST':
        correo = request.POST.get('correo')
        clave = request.POST.get('clave')

        try:
            response = requests.post(
                "http://127.0.0.1:8001/usuarios/login",
                json={"correo": correo, "contrasena": clave},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                request.session['usuario_id'] = data['id_usuario']
                request.session['usuario_nombre'] = data['nombre']
                request.session['usuario_rol'] = data['rol']

                if data['rol'].lower() == 'admin':
                    return redirect('panel_admin')
                else:
                    return redirect('panel_cliente')
            else:
                mensaje = 'Correo o contraseña incorrectos'

        except requests.RequestException:
            mensaje = 'Error al conectar con el servidor de autenticación'

    return render(request, 'vistas/login.html', {'mensaje': mensaje})

# Logout
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')

# Panel Admin
def panel_admin(request):
    nombre = request.session.get('usuario_nombre', '')

    # 🔔 Mensajes sin leer
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM mensajes_contacto WHERE leido = FALSE")
        mensajes_nuevos = cursor.fetchone()[0] > 0

    # 📋 Reservas pendientes
    reservas_pendientes = Reserva.objects.select_related('usuario', 'cabana').filter(estado='Pendiente')

    # 💬 Últimos 10 comentarios
    comentarios_recientes = Comentario.objects.order_by('-fecha')[:10]

    return render(request, 'panelAdmin.html', {
        'nombre': nombre,
        'hay_mensajes_nuevos': mensajes_nuevos,
        'reservas_pendientes': reservas_pendientes,
        'comentarios_recientes': comentarios,
    })

# Marcar mensajes leídos
def marcar_mensajes_leidos(request):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE mensajes_contacto SET leido = TRUE WHERE leido = FALSE")
    return redirect('/admin/app/mensajecontacto/')

# Panel Cliente
def panel_cliente(request):
    nombre = request.session.get('usuario_nombre', '')
    cabanas = Cabana.objects.filter(estado='Disponible')
    return render(request, 'panelCliente.html', {'nombre': nombre, 'cabanas': cabanas})

# Ver cabañas
def ver_cabanas(request):
    nombre = request.session.get('usuario_nombre', '')
    cabanas = Cabana.objects.order_by('estado')
    return render(request, 'vistas/cabanas.html', {'nombre': nombre, 'cabanas': cabanas})

# Formulario de reserva
def reservar_formulario(request):
    return render(request, 'vistas/reservas.html')

# Crear reserva
def reservar_cabana(request, id_cabana):
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        usuario_id = request.session.get("usuario_id")
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        cabana = get_object_or_404(Cabana, id_cabana=id_cabana)

        Reserva.objects.create(
            usuario=usuario,
            cabana=cabana,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='Pendiente'
        )
        messages.success(request, 'Reserva realizada correctamente.')
        return redirect('panel_cliente')

    return render(request, 'reservar.html')

# Confirmar o rechazar reserva
def confirmar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    reserva.estado = 'Confirmada'
    reserva.save()
    messages.success(request, f"✅ Reserva #{reserva_id} confirmada exitosamente.")
    return redirect('panel_admin')

def rechazar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    cabana = Cabana.objects.get(pk=reserva.cabana.id_cabana)
    reserva.delete()
    tiene_otra_reserva = Reserva.objects.filter(cabana=cabana).exists()
    if not Reserva.objects.filter(cabana=cabana).exists():
        cabana.estado = "Disponible"
        cabana.save()
    messages.success(request, "❌ Reserva rechazada correctamente. Cabaña disponible.")
    return redirect('panel_admin')

# Contacto
def contacto_view(request):
    nombre = request.session.get('usuario_nombre', '')
    return render(request, 'vistas/contacto.html', {'nombre': nombre})


def guardar_mensaje(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        mensaje = request.POST.get('mensaje')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO mensajes_contacto (nombre, correo, mensaje)
                VALUES (%s, %s, %s)
            """, [nombre, correo, mensaje])

        try:
            send_mail(
                subject='📩 Nuevo mensaje de contacto',
                message=f'Nombre: {nombre}\nCorreo: {correo}\n\nMensaje:\n{mensaje}',
                from_email='tunuevocorreo@gmail.com',
                recipient_list=['rodrigo01acr@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, '✅ Mensaje enviado correctamente.')
        except BadHeaderError:
            messages.error(request, '❌ Error al enviar el correo.')
        except Exception as e:
            messages.error(request, f'❌ Falló el envío: {e}')

        return redirect('contacto')

    return redirect('contacto')

# Comentarios
def comentarios(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        texto = request.POST.get('comentario', '').strip()
        estrellas = int(request.POST.get('estrellas', 0))

        if not nombre or not correo or not texto:
            messages.error(request, "❌ Todos los campos son obligatorios.")
        else:
            Comentario.objects.create(
                nombre=nombre,
                correo=correo,
                comentario=texto,
                estrellas=estrellas,
                fecha=timezone.now()
            )
            estrellas_visual = "★" * estrellas + "☆" * (5 - estrellas)
            messages.success(request, f"✅ ¡Gracias por tu comentario! {estrellas_visual}")
            return redirect('comentarios')

    comentarios = Comentario.objects.order_by('-fecha')
    nombre_usuario = request.session.get('usuario_nombre', '')
    return render(request, 'vistas/comentarios.html', {
        'comentarios': comentarios,
        'nombre': nombre_usuario
    })

# Crear cuenta y login automático
def crear_cuenta(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena1 = request.POST.get('contrasena1')
        contrasena2 = request.POST.get('contrasena2')

        if contrasena1 != contrasena2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, 'vistas/crear_cuenta.html')

        try:
            # Registro del usuario
            registro_resp = requests.post(
                "http://127.0.0.1:8001/usuarios/registro",
                json={
                    "nombre": nombre,
                    "correo": correo,
                    "contrasena": contrasena1,
                    "rol": "cliente"
                },
                timeout=5
            )

            if registro_resp.status_code == 200:
                # Login automático tras registro
                login_resp = requests.post(
                    "http://127.0.0.1:8001/usuarios/login",
                    json={
                        "correo": correo,
                        "contrasena": contrasena1
                    },
                    timeout=5
                )

                if login_resp.status_code == 200:
                    user_data = login_resp.json()
                    request.session['usuario_id'] = user_data['id_usuario']
                    request.session['usuario_nombre'] = user_data['nombre']
                    request.session['usuario_rol'] = user_data['rol']

                    messages.success(request, "Cuenta creada e iniciada sesión correctamente")
                    if user_data['rol'].lower() == 'admin':
                        return redirect('panel_admin')
                    else:
                        return redirect('panel_cliente')
                else:
                    messages.error(request, "Error al iniciar sesión después del registro")
            elif registro_resp.status_code == 400:
                detalle = registro_resp.json().get("detail", "Correo ya registrado")
                messages.error(request, detalle)
            else:
                messages.error(request, "No se pudo crear la cuenta. Intenta nuevamente.")

        except requests.RequestException:
            messages.error(request, "Error de conexión con el servidor de usuarios")

    return render(request, 'vistas/crear_cuenta.html')


# Transferencia de pago
def pago_transferencia(request):
    nombre = request.session.get('usuario_nombre', '')
    return render(request, 'vistas/pago_transferencia.html', {'nombre': nombre})





def inventario_view(request):
    cabanas = Cabana.objects.all()
    cabana_id = request.GET.get('cabana_id')
    inventario = []
    cabana_seleccionada = None

    if cabana_id:
        cabana_seleccionada = Cabana.objects.filter(id_cabana=cabana_id).first()
        inventario = Inventario.objects.filter(cabana_id=cabana_id)

    return render(request, 'vistas/inventario.html', {
        'cabanas': cabanas,
        'cabana_seleccionada': cabana_seleccionada,
        'inventario': inventario,
    })


@csrf_exempt
def guardar_inventario_estado(request):
    if request.method == 'POST':
        accion = request.POST.get("accion")  # aquí detectamos si es guardar o eliminar
        cabana_id = request.POST.get("cabana_id")
        seleccionados = request.POST.getlist("seleccionados")

        if accion == "eliminar":
            for item_id in seleccionados:
                try:
                    Inventario.objects.get(id_item=item_id).delete()
                except Inventario.DoesNotExist:
                    continue
            return JsonResponse({"status": "ok", "accion": "eliminado"})

        # Si no es eliminar, es guardar cambios
        for item_id in seleccionados:
            cantidad = request.POST.get(f"cantidad_{item_id}")
            estado = request.POST.get(f"estado_{item_id}")
            observacion = request.POST.get(f"observacion_{item_id}")

            try:
                inventario = Inventario.objects.get(id_item=item_id)
                inventario.cantidad = cantidad
                inventario.ubicacion = estado  
                inventario.observacion = observacion
                inventario.save()
            except Inventario.DoesNotExist:
                continue

        # Agregar nuevo objeto si viene del formulario adicional
        nuevo_nombre = request.POST.get("nuevo_nombre")
        nuevo_cantidad = request.POST.get("nuevo_cantidad")
        nuevo_estado = request.POST.get("nuevo_estado")
        nuevo_observacion = request.POST.get("nuevo_observacion")

        if nuevo_nombre and nuevo_cantidad and nuevo_estado:
            Inventario.objects.create(
                nombre=nuevo_nombre,
                cantidad=nuevo_cantidad,
                ubicacion=nuevo_estado,
                observacion=nuevo_observacion,
                cabana_id=cabana_id
            )

        return JsonResponse({"status": "ok", "accion": "guardado"})

    return JsonResponse({"status": "error", "message": "Método no permitido"})




def descargar_informe(request):
    tipo = request.GET.get('tipo', 'pdf')  # Puede ser 'pdf' o 'excel'

    if tipo == 'excel':
        return generar_excel()
    else:
        return generar_pdf()


def generar_excel():
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    hoja = workbook.add_worksheet("Resumen")

    hoja.write("A1", "Inventario bajo")
    hoja.write("A2", "Objeto")
    hoja.write("B2", "Cantidad")
    fila = 3
    for item in Inventario.objects.filter(cantidad__lt=5):
        hoja.write(f"A{fila}", item.nombre)
        hoja.write(f"B{fila}", item.cantidad)
        fila += 1

    hoja.write(f"A{fila+1}", "Reservas Confirmadas")
    hoja.write(f"A{fila+2}", "ID")
    hoja.write(f"B{fila+2}", "Usuario")
    hoja.write(f"C{fila+2}", "Estado")
    fila += 3
    for r in Reserva.objects.all():
        hoja.write(f"A{fila}", r.id_reserva)
        hoja.write(f"B{fila}", r.usuario.nombre)
        hoja.write(f"C{fila}", r.estado)
        fila += 1

    workbook.close()
    output.seek(0)

    return FileResponse(output, as_attachment=True, filename="informe.xlsx")


def generar_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    y = 800

    p.drawString(100, y, "Informe de Inventario bajo")
    y -= 20
    for item in Inventario.objects.filter(cantidad__lt=5):
        p.drawString(100, y, f"{item.nombre} - {item.cantidad} unidades")
        y -= 15

    y -= 20
    p.drawString(100, y, "Reservas")
    y -= 20
    for r in Reserva.objects.all():
        p.drawString(100, y, f"#{r.id_reserva} - {r.usuario.nombre} - {r.estado}")
        y -= 15

    y -= 20
    p.drawString(100, y, "Promedio de estrellas:")
    promedio = Comentario.objects.aggregate(promedio=Avg('estrellas'))['promedio'] or 0
    p.drawString(100, y - 15, f"{round(promedio, 2)} / 5")

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="informe.pdf")



def panel_admin(request):
    nombre = request.session.get('usuario_nombre', '')

    # 🔔 Mensajes sin leer
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM mensajes_contacto WHERE leido = FALSE")
        mensajes_nuevos = cursor.fetchone()[0] > 0

    # 📋 Reservas pendientes
    reservas_pendientes = Reserva.objects.select_related('usuario', 'cabana').filter(estado='Pendiente')

    # 💬 Comentarios de los últimos 15 días
    hace_15_dias = timezone.now() - timedelta(days=15)
    comentarios = Comentario.objects.filter(fecha__gte=hace_15_dias).order_by('-fecha')

    return render(request, 'panelAdmin.html', {
        'nombre': nombre,
        'hay_mensajes_nuevos': mensajes_nuevos,
        'reservas_pendientes': reservas_pendientes,
        'comentarios_recientes': comentarios,
    })


# Listar todas las cabañas (vista principal del admin)
def admin_cabanas(request):
    cabanas = Cabana.objects.all()
    return render(request, 'vistas/admin_cabanas.html', {'cabanas': cabanas})

# Crear nueva cabaña
def crear_cabana(request):
    if request.method == 'POST':
        form = CabanaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_cabanas')
    else:
        form = CabanaForm()
    return render(request, 'vistas/form_cabana.html', {'form': form, 'accion': 'Crear'})

# Editar cabaña existente
def editar_cabana(request, id_cabana):
    cabana = get_object_or_404(Cabana, id_cabana=id_cabana)
    if request.method == 'POST':
        form = CabanaForm(request.POST, instance=cabana)
        if form.is_valid():
            form.save()
            return redirect('admin_cabanas')
    else:
        form = CabanaForm(instance=cabana)
    return render(request, 'vistas/form_cabana.html', {'form': form, 'accion': 'Editar'})

# Eliminar cabaña
def eliminar_cabana(request, id_cabana):
    cabana = get_object_or_404(Cabana, id_cabana=id_cabana)
    cabana.delete()
    return redirect('admin_cabanas')

# Lisrtar pagos
def listar_pagos(request):
    pagos = Pago.objects.all()
    return render(request, 'vistas/listar_pagos.html', {'pagos': pagos})

# Listar reservas
def listar_reservas(request):
    reservas = Reserva.objects.select_related('usuario', 'cabana').all()
    return render(request, 'vistas/listar_reservas.html', {'reservas': reservas})

# Exportar reservas a CSV
def exportar_reservas_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservas.csv"'

    # Agregar BOM al inicio del archivo CSV
    response.write('\ufeff')  # Esto asegura que Excel reconozca correctamente la codificación UTF-8

    writer = csv.writer(response)
    writer.writerow(['ID', 'Usuario', 'Cabaña', 'Fecha Inicio', 'Fecha Fin', 'Estado'])

    reservas = Reserva.objects.all()
    for reserva in reservas:
        writer.writerow([
            reserva.id_reserva,
            reserva.usuario.nombre,
            reserva.cabana.nombre,
            reserva.fecha_inicio,
            reserva.fecha_fin,
            reserva.estado
        ])

    return response

# Listar usuarios:
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'vistas/listar_usuarios.html', {'usuarios': usuarios})