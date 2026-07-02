from django.db import models


class TestProyecto(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=30)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    version_actual = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    creado_por = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_proyecto'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TestModulo(models.Model):
    id = models.BigAutoField(primary_key=True)
    proyecto = models.ForeignKey(TestProyecto, models.DO_NOTHING, related_name='modulos')
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    prioridad = models.CharField(max_length=5, blank=True, null=True)
    estado = models.CharField(max_length=8, blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_modulo'
        ordering = ['-fecha_creacion']
        unique_together = (('proyecto', 'codigo'),)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TestRequerimiento(models.Model):
    id = models.BigAutoField(primary_key=True)
    modulo = models.ForeignKey(TestModulo, models.DO_NOTHING, related_name='requerimientos')
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=12, blank=True, null=True)
    prioridad = models.CharField(max_length=5, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_requerimiento'
        ordering = ['-fecha_creacion']
        unique_together = (('modulo', 'codigo'),)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TestCaso(models.Model):
    id = models.BigAutoField(primary_key=True)
    requerimiento = models.ForeignKey(TestRequerimiento, models.DO_NOTHING, related_name='casos')
    codigo = models.CharField(max_length=40)
    titulo = models.CharField(max_length=400)
    objetivo = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precondiciones = models.TextField(blank=True, null=True)
    datos_prueba = models.TextField(blank=True, null=True)
    resultado_esperado = models.TextField(blank=True, null=True)
    prioridad = models.CharField(max_length=7, blank=True, null=True)
    tipo = models.CharField(max_length=10, blank=True, null=True)
    estado = models.CharField(max_length=8, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    activo = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_caso'
        ordering = ['-fecha_creacion']
        unique_together = (('requerimiento', 'codigo'),)

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'


class TestPlan(models.Model):
    id = models.BigAutoField(primary_key=True)
    proyecto = models.ForeignKey(TestProyecto, models.DO_NOTHING, related_name='planes')
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=30, blank=True, null=True)
    ambiente = models.CharField(max_length=10, blank=True, null=True)
    estado = models.CharField(max_length=12, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    responsable = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_plan'
        ordering = ['-fecha_creacion']
        unique_together = (('proyecto', 'codigo'),)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TestPlanCaso(models.Model):
    id = models.BigAutoField(primary_key=True)
    plan = models.ForeignKey(TestPlan, models.DO_NOTHING, related_name='plan_casos')
    caso = models.ForeignKey(TestCaso, models.DO_NOTHING, related_name='plan_casos')
    orden = models.IntegerField(blank=True, null=True)
    obligatorio = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_plan_caso'
        ordering = ['orden', 'fecha_creacion']
        unique_together = (('plan', 'caso'),)

    def __str__(self):
        return f'{self.plan.codigo} -> {self.caso.codigo}'


class TestPaso(models.Model):
    id = models.BigAutoField(primary_key=True)
    caso = models.ForeignKey(TestCaso, models.DO_NOTHING, related_name='pasos')
    numero = models.IntegerField()
    accion = models.TextField()
    datos = models.TextField(blank=True, null=True)
    resultado_esperado = models.TextField()
    obligatorio = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_paso'
        ordering = ['numero', 'fecha_creacion']
        unique_together = (('caso', 'numero'),)

    def __str__(self):
        return f'Paso {self.numero} - {self.caso.codigo}'


class TestEjecucion(models.Model):
    id = models.BigAutoField(primary_key=True)
    plan_caso = models.ForeignKey(TestPlanCaso, models.DO_NOTHING, related_name='ejecuciones')
    numero_ejecucion = models.IntegerField(blank=True, null=True)
    ejecutado_por = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    duracion_segundos = models.IntegerField(blank=True, null=True)
    resultado = models.CharField(max_length=12, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    navegador = models.CharField(max_length=100, blank=True, null=True)
    sistema_operativo = models.CharField(max_length=100, blank=True, null=True)
    ip_cliente = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_ejecucion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Ejecución {self.id}'


class TestBug(models.Model):
    id = models.BigAutoField(primary_key=True)
    ejecucion = models.ForeignKey(TestEjecucion, models.DO_NOTHING, related_name='bugs')
    codigo = models.CharField(unique=True, max_length=30)
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, null=True)
    severidad = models.CharField(max_length=7, blank=True, null=True)
    prioridad = models.CharField(max_length=5, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    responsable = models.IntegerField(blank=True, null=True)
    fecha_reporte = models.DateTimeField(blank=True, null=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_bug'
        ordering = ['-fecha_reporte']

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'


class TestEvidencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    ejecucion = models.ForeignKey(TestEjecucion, models.DO_NOTHING, related_name='evidencias')
    tipo = models.CharField(max_length=6, blank=True, null=True)
    nombre_original = models.CharField(max_length=300, blank=True, null=True)
    nombre_archivo = models.CharField(max_length=300, blank=True, null=True)
    ruta = models.CharField(max_length=600, blank=True, null=True)
    mime_type = models.CharField(max_length=150, blank=True, null=True)
    tamano = models.BigIntegerField(blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_evidencia'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre_archivo or self.id}'
