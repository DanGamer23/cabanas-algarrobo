"""
URL configuration for cabanas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('cliente-panel/', views.panel_cliente, name='panel_cliente'),
    path('reservar/<int:id_cabana>/', views.reservar_cabana, name='reservar_cabana'),

    path('cabanas/', views.ver_cabanas, name='ver_cabanas'),
    path('reservas/', views.reservar_formulario, name='reservas'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('comentarios/', views.comentarios, name='comentarios'),
    path('crear-cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('pago-transferencia/', views.pago_transferencia, name='pago_transferencia'),

    path('guardar-mensaje/', views.guardar_mensaje, name='guardar_mensaje'),

    path('mensajes/marcar-leidos/', views.marcar_mensajes_leidos, name='marcar_mensajes_leidos'),

    path('reservas/confirmar/<int:reserva_id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservas/rechazar/<int:reserva_id>/', views.rechazar_reserva, name='rechazar_reserva'),

    path('comentarios/', views.comentarios, name='comentarios'),

    path('inventario/', views.inventario_view, name='inventario_view'),
    path('guardar-inventario/', views.guardar_inventario_estado, name='guardar_inventario_estado'),
    path('inventario/', views.inventario_view, name='inventario'),

    path('descargar-informe/', views.descargar_informe, name='descargar_informe'),
    path('panel/cabanas/', views.admin_cabanas, name='admin_cabanas'),
    path('panel/cabanas/crear/', views.crear_cabana, name='crear_cabana'),
    path('panel/cabanas/editar/<int:id_cabana>/', views.editar_cabana, name='editar_cabana'),
    path('panel/cabanas/eliminar/<int:id_cabana>/', views.eliminar_cabana, name='eliminar_cabana'),
    path('panel/pagos/', views.listar_pagos, name='listar_pagos'),
    path('panel/pagos/confirmar/<int:id_pago>/', views.confirmar_pago, name='confirmar_pago'),
    path('panel/pagos/exportar/', views.exportar_pagos_excel, name='exportar_pagos'),
    path('panel/reservas/', views.listar_reservas, name='listar_reservas'),
    path('panel/reservas/exportar/', views.exportar_reservas_csv, name='exportar_reservas'),
    path('panel/usuarios/', views.listar_usuarios, name='listar_usuarios'),

]


urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
