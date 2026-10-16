//======================================================================
// Funcion para cerrar ventanas modales
//======================================================================
function cerrarModal(idModal) {
    $('#' + idModal).modal('hide');
}

$(document).ready(function () {
    //======================================================================
    // MODAL INSPECTOR 
    //======================================================================
    $('#update_Inspector').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget);
        let id = button.data('id');
        let nombre = button.data('nombre');
        let apellido = button.data('descripcion');

        let modal = $(this);
        modal.find('#IDINSPECTOREditHIDDEN').val(id);
        modal.find('#NOMBREEdit').val(nombre);
        modal.find('#APELLIDOEdit').val(apellido);
    });

    $('#delete_Inspector').on('show.bs.modal', function (event) {
            let button = $(event.relatedTarget);
            let id = button.data('id');
            let nombre = button.data('nombre');
            let apellido = button.data('descripcion');

            let modal = $(this);
            modal.find('#IDINSPECTORDelHIDDEN').val(id);

            // Cambiar el título
            modal.find('.modal-title2').text('¿Estás seguro de eliminar el Inspector: ' + apellido +  ','  + nombre + ' ?');
            modal.find('#NOMBREDel').val(nombre);
            modal.find('#APELLIDODel').val(apellido);
    });

    /*//======================================================================
    // MODAL RECLAMO - ACTUALIZAR
    //======================================================================
    $('#modalReclamo').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget);

        let id = button.data('id');
        let expediente = button.data('expediente');
        let comercio = button.data('comercio');
        let denunciante = button.data('denunciante');
        let fecha = button.data('fecha');
        let descripcion = button.data('descripcion');
        let estado = button.data('estado');
        let prioridad = button.data('prioridad');

        let modal = $(this);
        // ID oculto
        modal.find('#idReclamoEdit').val(id);

        // Textos informativos de contexto
        modal.find('#expedienteReclamoText').text(expediente || 'S/N');
        modal.find('#comercioReclamoText').text(comercio || 'No especificado');
        modal.find('#denuncianteReclamoText').text(denunciante || 'Anónimo');
        modal.find('#fechaReclamoText').text(fecha || '-');

        // Campos editables
        modal.find('#descripcionReclamoEdit').val(descripcion || '');
        modal.find('#estadoReclamoEdit').val(estado);
        modal.find('#prioridadReclamoEdit').val(prioridad ? 'true' : 'false');
    });*/

    //======================================================================
    // MODAL RECLAMO - ACTUALIZAR
    //======================================================================
    $('#modalReclamo').on('show.bs.modal', async function (event) {
        let button = $(event.relatedTarget);
        if (!button.length) return;

        let idReclamo = button.data('id');

        if (!idReclamo) return;

        // Reseteamos las solapas a la primera (Gestión)
        $('#tabsReclamo a[href="#tab-gestion"]').tab('show');

        // Llamamos a la función que busca toda la información en el backend
        await cargarDatosReclamoModal(idReclamo);
    });

});