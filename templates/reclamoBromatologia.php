<?php
// Configuración de conexión a la base de datos
$host     = 'localhost';
$db       = 'bromatologiaReclamos';
$user     = 'root';
$pass     = '';
$charset  = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);

    // Consulta de Localidades (tabla en InnoDB)
    $stmtLocalidades = $pdo->query("SELECT IdLocalidad, nombre FROM Localidad ORDER BY nombre ASC");
    $localidades = $stmtLocalidades->fetchAll();

    // Consulta de Categorías activas ordenadas
    $stmtCategorias = $pdo->query("SELECT idCategoriaReclamo, nombre, requiereDetalle FROM CategoriaReclamo WHERE activa = 1 ORDER BY orden ASC");
    $categorias = $stmtCategorias->fetchAll();

} catch (\PDOException $e) {
    die("Error al conectar con la base de datos: " . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Oficina de Bromatología - Formulario de Reclamos</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
    body { background-color: #f7f9fa; color: #333333; padding: 30px 15px; }
    .form-container { max-width: 840px; margin: 0 auto; background: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 35px 40px; }
    
    /* Header formal sin barra de navegación */
    .header-box { margin-bottom: 25px; border-bottom: 1px solid #e0e0e0; padding-bottom: 15px; }
    .header-box h1 { font-size: 20px; font-weight: 700; color: #263238; text-transform: uppercase; letter-spacing: 0.5px; }
    .header-box p { font-size: 13px; color: #666; margin-top: 4px; }
    
    /* Estética institucional: separadores turquesa de 9 de Julio */
    .section-title { font-size: 16px; font-weight: 700; color: #263238; margin-top: 30px; margin-bottom: 8px; }
    .section-divider { width: 100%; height: 3px; background-color: #00897b; margin-bottom: 22px; }
    
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 700; color: #222; margin-bottom: 6px; }
    .form-group label span.req { color: #d32f2f; }
    .form-group label span.opt { font-weight: normal; color: #777; font-size: 12px; }
    
    .form-control { width: 100%; padding: 9px 12px; font-size: 14px; border: 1px solid #cccccc; border-radius: 3px; background-color: #fff; outline: none; transition: border-color 0.2s; }
    .form-control:focus { border-color: #00897b; }
    
    .form-row { display: flex; gap: 15px; }
    .form-row .form-group { flex: 1; }
    
    /* Grilla de checkboxes para categorías */
    .categories-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; margin-bottom: 20px; }
    .category-card { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 10px 14px; display: flex; align-items: flex-start; gap: 10px; cursor: pointer; transition: background 0.15s, border-color 0.15s; }
    .category-card:hover { background: #f0f7f6; border-color: #80cbc4; }
    .category-card input[type="radio"] { margin-top: 3px; accent-color: #00897b; }
    .category-card span { font-size: 13.5px; font-weight: 500; color: #37474f; }
    
    /* Panel condicional para alimento vencido / en mal estado */
    #panel_alimento_mal_estado { display: none; background: #fffde7; border: 1.5px solid #fff59d; border-radius: 4px; padding: 20px; margin-bottom: 25px; }
    .panel-alimento-title { font-size: 14px; font-weight: 700; color: #f57f17; text-transform: uppercase; margin-bottom: 12px; }
    .help-hint { font-size: 12px; color: #616161; margin-top: 4px; line-height: 1.4; }
    
    /* Teléfono con estilo de 9 de Julio */
    .phone-inputs { display: flex; gap: 10px; }
    .phone-inputs .cod-area { width: 30%; }
    .phone-inputs .num-tel { width: 70%; }
    
    /* Alerta informativa */
    .info-alert { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 12px; font-size: 12.5px; color: #0d47a1; margin: 12px 0; border-radius: 2px; }
    
    /* Botones de acción institucional */
    .btn-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 35px; border-top: 1px solid #e0e0e0; padding-top: 25px; }
    .btn { padding: 10px 24px; font-size: 14px; font-weight: 600; border-radius: 3px; border: none; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; text-decoration: none; display: inline-block; text-align: center; }
    .btn-cancel { background-color: #546e7a; color: #fff; }
    .btn-cancel:hover { background-color: #455a64; }
    .btn-submit { background-color: #00897b; color: #fff; }
    .btn-submit:hover { background-color: #00796b; }
    
    @media (max-width: 650px) {
      .form-row, .categories-grid { display: flex; flex-direction: column; }
    }
  </style>
</head>
<body>

<div class="form-container">
  <div class="header-box">
    <h1>Oficina de Bromatología</h1>
    <p>Formulario Web de Reclamos sobre Comercios y Control de Alimentos</p>
  </div>

  <form id="reclamoForm" action="http://localhost:5000/procesar_reclamo.py" method="POST" enctype="multipart/form-data">

    <!-- 1. DATOS DEL COMERCIO Y UBICACIÓN -->
    <div class="section-title">Datos del Comercio Reclamado</div>
    <div class="section-divider"></div>

    <div class="form-row">
      <div class="form-group" style="flex: 2;">
        <label>Nombre de Fantasía o Razón Social <span class="req">*</span></label>
        <input type="text" name="comercioNombre" class="form-control" placeholder="Ej: Supermercado Central" required>
      </div>

      <div class="form-group" style="flex: 1;">
        <label>Localidad del Partido <span class="req">*</span></label>
        <select name="idLocalidad" class="form-control" required>
          <option value="">-- Seleccionar --</option>
          <?php foreach ($localidades as $loc): ?>
            <option value="<?= htmlspecialchars($loc['IdLocalidad']) ?>">
              <?= htmlspecialchars($loc['nombre']) ?>
            </option>
          <?php endforeach; ?>
        </select>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group" style="flex: 3;">
        <label>Calle <span class="req">*</span></label>
        <input type="text" name="calle" class="form-control" placeholder="Nombre de la calle" required>
      </div>

      <div class="form-group" style="flex: 1;">
        <label>N° Calle <span class="opt">(Si posee)</span></label>
        <input type="number" name="nroCalle" class="form-control" placeholder="Ej: 1250">
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>Entre Calle <span class="opt">(Opcional)</span></label>
        <input type="text" name="calleEntre" class="form-control" placeholder="Primera intersección">
      </div>

      <div class="form-group">
        <label>Y Calle <span class="opt">(Opcional)</span></label>
        <input type="text" name="calleEntre2" class="form-control" placeholder="Segunda intersección">
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>Latitud GPS <span class="opt">(Puestos/Ferias ambulantes)</span></label>
        <input type="text" name="latitud" class="form-control" placeholder="-35.4445">
      </div>
      <div class="form-group">
        <label>Longitud GPS <span class="opt">(Puestos/Ferias ambulantes)</span></label>
        <input type="text" name="longitud" class="form-control" placeholder="-60.8831">
      </div>
    </div>

    <!-- 2. CATEGORÍA DEL RECLAMO -->
    <div class="section-title">Categoría del Reclamo</div>
    <div class="section-divider"></div>
    <label style="font-size: 13px; font-weight: 700;">Seleccione el motivo del reclamo <span class="req">*</span></label>

    <div class="categories-grid">
      <?php foreach ($categorias as $cat): ?>
        <label class="category-card">
          <input type="radio" 
                 name="idCategoriaReclamo" 
                 value="<?= htmlspecialchars($cat['idCategoriaReclamo']) ?>" 
                 data-nombre="<?= strtolower(htmlspecialchars($cat['nombre'])) ?>"
                 data-requieredetalle="<?= $cat['requiereDetalle'] ?>"
                 onchange="evaluarCategoria(this)"
                 required>
          <span><?= htmlspecialchars($cat['nombre']) ?></span>
        </label>
      <?php endforeach; ?>
    </div>

    <!-- Campo adicional obligatorio si selecciona "Otros" -->
    <div class="form-group" id="grupo_otro_detalle" style="display: none;">
      <label>Especifique el motivo particular <span class="req">*</span></label>
      <input type="text" name="categoriaDetalle" id="categoriaDetalle" class="form-control" placeholder="Indique la anomalía observada">
    </div>

    <!-- 3. PANEL ESPECÍFICO: ALIMENTO EN MAL ESTADO O VENCIDO -->
    <div id="panel_alimento_mal_estado">
      <div class="panel-alimento-title">Detalle Específico del Alimento Reclamado</div>
      
      <div class="form-group">
        <label>Nombre y Marca del Producto <span class="req">*</span></label>
        <input type="text" name="productoNombreMarca" id="prod_nombre_marca" class="form-control" placeholder="Ej: Yogur descremado marca La Serenísima, pote 200g">
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Fecha de Vencimiento impresa <span class="opt">(Si figura)</span></label>
          <input type="date" name="fechaVencimiento" id="prod_vencimiento" class="form-control">
        </div>

        <div class="form-group">
          <label>N° de Lote <span class="opt">(Si figura en el envase)</span></label>
          <input type="text" name="nroLote" id="prod_lote" class="form-control" placeholder="Ej: LOTE-302B">
        </div>
      </div>

      <div class="form-group">
        <label>Estado de Conservación y Almacenamiento <span class="req">*</span></label>
        <textarea name="estadoConservacion" id="prod_conservacion" class="form-control" rows="3" placeholder="Indique cómo se encontraba exhibido al comprarlo..."></textarea>
        <div class="help-hint">Indique cómo se encontraba almacenado o exhibido el producto al momento de la compra. Si requería refrigeración, especifique si se encontraba en una góndola o equipo de frío y, de ser posible, si la temperatura de conservación era adecuada.</div>
      </div>
    </div>

    <!-- 4. DETALLE DEL HECHO -->
    <div class="section-title">Detalle del Hecho y Descripción</div>
    <div class="section-divider"></div>

    <div class="form-group">
      <label>Fecha y Hora en que ocurrió o fue adquirido <span class="req">*</span></label>
      <input type="datetime-local" name="fechaHoraHecho" class="form-control" required>
    </div>

    <div class="form-group">
      <label>Descripción detallada de lo sucedido o del problema detectado <span class="req">*</span></label>
      <textarea name="descripcionProblema" class="form-control" rows="4" placeholder="Describa el olor, sabor, estado del envase, falta de higiene o situación presenciada." required></textarea>
    </div>

    <!-- 5. EVIDENCIAS RESPALDATORIAS -->
    <div class="section-title">Evidencias Respaldatorias</div>
    <div class="section-divider"></div>

    <div class="form-group">
      <label>Adjuntar Fotos del Producto, Etiquetas, Ticket de Compra o Local <span class="opt">(Opcional)</span></label>
      <input type="file" name="evidencias[]" multiple class="form-control" accept="image/*,video/*,.pdf">
      <div class="help-hint">Formatos soportados: JPG, PNG, PDF. Se aconseja fotografiar fecha de vencimiento y número de lote.</div>
    </div>

    <!-- 6. MODALIDAD DE IDENTIFICACIÓN -->
    <div class="section-title">Modalidad de Identificación del Reclamante</div>
    <div class="section-divider"></div>

    <div class="form-row" style="margin-bottom: 12px;">
      <label style="display: inline-flex; align-items: center; gap: 8px; font-weight: 600; cursor: pointer;">
        <input type="radio" name="esAnonimo" value="0" checked onchange="toggleAnonimo(this.value)" style="accent-color: #00897b;">
        Reclamo Identificado (Permite seguimiento del caso)
      </label>
      <label style="display: inline-flex; align-items: center; gap: 8px; font-weight: 600; cursor: pointer;">
        <input type="radio" name="esAnonimo" value="1" onchange="toggleAnonimo(this.value)" style="accent-color: #00897b;">
        Reclamo Anónimo
      </label>
    </div>

    <div id="aviso_anonimo" class="info-alert" style="display: none;">
      <strong>Aviso de Reclamo Anónimo:</strong> El reclamo se inspeccionará de oficio, pero no le permitirá recibir actualizaciones del resultado de la inspección.
    </div>

    <div id="campos_denunciante">
      <div class="form-row">
        <div class="form-group">
          <label>Nombre <span class="req">*</span></label>
          <input type="text" name="nomDenunciante" id="nomDenunciante" class="form-control">
        </div>
        <div class="form-group">
          <label>Apellido <span class="req">*</span></label>
          <input type="text" name="apeDenunciante" id="apeDenunciante" class="form-control">
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Teléfono (CELULAR CON WHATSAPP) - SIN 0 Y SIN 15 <span class="req">*</span></label>
          <div class="phone-inputs">
            <input type="number" name="areaCelDenunciante" id="areaCelDenunciante" class="form-control cod-area" placeholder="Área (sin 0)">
            <input type="number" name="nroCelDenunciante" id="nroCelDenunciante" class="form-control num-tel" placeholder="Nro. (sin 15)">
          </div>
        </div>

        <div class="form-group">
          <label>Correo Electrónico <span class="req">*</span></label>
          <input type="email" name="emailDenunciante" id="emailDenunciante" class="form-control" placeholder="su-correo@dominio.com">
        </div>
      </div>
    </div>

    <!-- 7. DECLARACIÓN JURADA -->
    <div class="form-group" style="margin-top: 25px;">
      <label style="font-weight: normal; font-size: 13px; display: inline-flex; gap: 8px; cursor: pointer;">
        <input type="checkbox" name="aceptaDeclaracionJurada" value="1" required style="accent-color: #00897b;">
        Declaro bajo juramento la veracidad de los datos suministrados en este reclamo para su intervención por Bromatología (Ley 25.326).
      </label>
    </div>

    <!-- BOTONES -->
    <div class="btn-actions">
      <a href="javascript:history.back()" class="btn btn-cancel">Cancelar</a>
      <button type="submit" class="btn btn-submit">Ingresar Reclamo</button>
    </div>

  </form>
</div>

<script>
  // Evaluar selección de categorías
  function evaluarCategoria(radio) {
    const nombre = radio.getAttribute('data-nombre');
    const requiereDetalle = radio.getAttribute('data-requieredetalle');
    
    const panelAlimento = document.getElementById('panel_alimento_mal_estado');
    const prodNombreMarca = document.getElementById('prod_nombre_marca');
    const prodConservacion = document.getElementById('prod_conservacion');

    const grupoOtro = document.getElementById('grupo_otro_detalle');
    const inputOtro = document.getElementById('categoriaDetalle');

    // Despliegue de campos para Alimento vencido / en mal estado
    if (nombre.includes('vencid') || nombre.includes('mal estado')) {
      panelAlimento.style.display = 'block';
      prodNombreMarca.required = true;
      prodConservacion.required = true;
    } else {
      panelAlimento.style.display = 'none';
      prodNombreMarca.required = false;
      prodConservacion.required = false;
      prodNombreMarca.value = '';
      prodConservacion.value = '';
    }

    // Despliegue de detalle si es categoría "Otros"
    if (requiereDetalle === '1' || nombre === 'otros') {
      grupoOtro.style.display = 'block';
      inputOtro.required = true;
    } else {
      grupoOtro.style.display = 'none';
      inputOtro.required = false;
      inputOtro.value = '';
    }
  }

  // Manejo de opción anónimo / identificado
  function toggleAnonimo(esAnonimo) {
    const campos = document.getElementById('campos_denunciante');
    const aviso = document.getElementById('aviso_anonimo');
    const inputs = [
      document.getElementById('nomDenunciante'),
      document.getElementById('apeDenunciante'),
      document.getElementById('areaCelDenunciante'),
      document.getElementById('nroCelDenunciante'),
      document.getElementById('emailDenunciante')
    ];

    if (esAnonimo === '1') {
      campos.style.display = 'none';
      aviso.style.display = 'block';
      inputs.forEach(el => { el.required = false; el.value = ''; });
    } else {
      campos.style.display = 'block';
      aviso.style.display = 'none';
      inputs.forEach(el => { el.required = true; });
    }
  }

  // Inicializar estado requerido
  toggleAnonimo('0');
</script>

</body>
</html>