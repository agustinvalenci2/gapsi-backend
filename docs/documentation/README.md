# Coleccion de Postman: GAPSI

Importa [GAPSI.postman_collection.json](../collections/GAPSI.postman_collection.json)
desde **Import** en Postman. La API debe estar disponible en `http://localhost:8000`.
No necesitas importar un entorno: las variables estan definidas en la coleccion.

## Ejecucion

1. Ejecuta Health para comprobar la API.
2. Ejecuta Auth en orden: registro, login y consulta del usuario.
3. Ejecuta Incidencias en orden: crear, listar, consultar, actualizar, resumen, eliminar y verificar eliminacion.

Puedes ejecutar la coleccion completa con Collection Runner, respetando ese orden.
Los scripts verifican los codigos HTTP esperados, guardan el JWT despues del login
y el ID despues de crear la incidencia. Todas las rutas privadas heredan Bearer Auth.

Cada registro genera un username y correo nuevos para evitar duplicados al repetir
la coleccion. Crea un usuario persistente por ejecucion; el ultimo paso elimina
solo la incidencia creada en el ejemplo. Para usar un usuario existente, configura
`generate_user=false`, completa `username` y `password`, y omite el registro.

## Variables de la coleccion

| Variable | Uso |
| --- | --- |
| `base_url` | Direccion de la API, sin barra final. Por defecto `http://localhost:8000`. |
| `generate_user` | `true` genera username y correo antes del registro. |
| `username` | Nombre de usuario para registro y login. |
| `email` | Correo para registro. |
| `password` | Contrasena de ejemplo; puedes cambiarla. |
| `access_token` | Se guarda automaticamente al iniciar sesion. |
| `incident_id` | Se guarda automaticamente al crear una incidencia. |

Evita variables de entorno con los mismos nombres, porque pueden sobrescribir
las variables de la coleccion. No compartas una exportacion con tokens o contrasenas reales.

## Endpoints

| Metodo | Ruta | Resultado esperado |
| --- | --- | --- |
| GET | `/health` | 200, estado de la API |
| POST | `/api/v1/auth/register` | 201, usuario creado |
| POST | `/api/v1/auth/login` | 200, JWT y vencimiento en segundos |
| GET | `/api/v1/auth/me` | 200, usuario autenticado |
| POST | `/api/v1/incidents` | 201, incidencia creada |
| GET | `/api/v1/incidents?offset=0&limit=20` | 200, incidencias propias |
| GET | `/api/v1/incidents/{id}` | 200, incidencia propia |
| PUT | `/api/v1/incidents/{id}` | 200, incidencia actualizada |
| GET | `/api/v1/incidents/summary` | 200, total y cantidades por estado |
| DELETE | `/api/v1/incidents/{id}` | 204, sin cuerpo |

El registro recibe JSON; el login recibe formulario `application/x-www-form-urlencoded`
con `username` y `password`. El resto de las operaciones con cuerpo usa JSON.

## Datos de incidencias

```json
{
  "title": "Error al ingresar",
  "description": "La pagina muestra un error",
  "priority": "high",
  "status": "pending"
}
```

Titulo: 1 a 100 caracteres. Descripcion: opcional, hasta 10000 caracteres.
Prioridades: `low`, `middle`, `high`; estados: `pending`, `done`, `rejected`.
Los valores iniciales son `low` y `pending`. PUT reemplaza los campos; los campos
opcionales omitidos vuelven a sus valores iniciales. El propietario viene del JWT;
no se admite `user_id` en el cuerpo.

Ejemplo del resumen (las cantidades dependen de los datos del usuario):

```json
{
  "total": 4,
  "by_status": { "pending": 2, "done": 1, "rejected": 1 }
}
```

El resumen cuenta todas las incidencias propias, sin paginacion, e incluye estados
sin incidencias con cero. El script verifica que el total coincida con la suma.

## Errores habituales

- 401: credenciales incorrectas o JWT ausente, invalido o expirado; ejecuta el login nuevamente.
- 404: incidencia inexistente, eliminada o perteneciente a otro usuario.
- 409: username o correo ya registrado.
- 422: cuerpo o parametros invalidos.

Despues del DELETE, la solicitud de verificacion espera 404 y cuenta como exitosa.
Swagger esta disponible en `http://localhost:8000/docs`.
