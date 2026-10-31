# Datos precargados de la aplicación.
# Para esta entrega no usamos base de datos: los lugares y las zonas están aquí, en listas de Python.

# Lugares turísticos a los que se puede ir. "lat" y "lng" son las coordenadas (latitud y longitud).
LUGARES = [
    {
        "id": "alegre",
        "nombre": "Cerro Alegre",
        "tipo": "cerro",
        "lat": -33.04342,
        "lng": -71.62985,
        "horario": "Abierto las 24 horas del día",
        "descripcion": "El Cerro Alegre es un emblemático barrio patrimonial de Valparaíso famoso por su arquitectura europea decimonónica, sus calles coloridas llenas de arte urbano, sus miradores hacia la bahía y su ambiente bohemio repleto de cafés, hoteles boutique y restoranes.",
        "fotos": ["alegre-1.jpg", "alegre-2.jpg"],
    },
    {
        "id": "concepcion",
        "nombre": "Cerro Concepción (Paseo Atkinson)",
        "tipo": "cerro",
        "lat": -33.04227,
        "lng": -71.6265,
        "horario": "Abierto las 24 horas del día",
        "descripcion": "El Cerro Concepción es un emblemático y turístico cerro de Valparaíso caracterizado por su arquitectura europea de origen británico y alemán, sus miradores (Atkinson y Gervasoni), su histórico ascensor, el arte urbano en sus escaleras y su bohemia oferta de cafés y galerías.",
        "fotos": ["concepcion-1.jpg"],
    },
    {
        "id": "bellavista",
        "nombre": "Cerro Bellavista",
        "tipo": "cerro",
        "lat": -33.05011,
        "lng": -71.6223,
        "horario": "Abierto las 24 horas del día",
        "descripcion": "El Cerro Bellavista es un artístico barrio de Valparaíso famoso por el Museo a Cielo Abierto —un circuito de 20 murales patrimoniales— y La Sebastiana, la célebre casa de Pablo Neruda. Es un sector residencial de gran valor cultural, conectado al plan de la ciudad por el histórico Ascensor Espíritu Santo y dueño de excelentes vistas al puerto.",
        "fotos": ["bellavista-1.jpg"],
    },
    {
        "id": "baburizza",
        "nombre": "Palacio Baburizza",
        "tipo": "museo",
        "lat": -33.0403,
        "lng": -71.62892,
        "horario": "Martes a domingo de 10:00 a 18:00 horas.",
        "descripcion": "Mansión de principios del siglo XX de estilo modernista y ecléctico ubicada en el Paseo Yugoslavo, que actualmente funciona como el Museo de Bellas Artes de Valparaíso.",
        "fotos": ["baburizza-1.jpg"],
    },
    {
        "id": "el-peral",
        "nombre": "Ascensor El Peral",
        "tipo": "ascensor",
        "lat": -33.03963,
        "lng": -71.62945,
        "horario": "Lunes a viernes: 07:00 a 22:00 hrs. Sábados, domingos y festivos: 08:00 a 22:00 hrs.",
        "descripcion": "Histórico funicular inaugurado en 1902 que conecta la Plaza de la Justicia con el Paseo Yugoslavo, declarado Monumento Nacional.",
        "fotos": ["elperal-1.jpg"],
    },
    {
        "id": "museo-maritimo",
        "nombre": "Museo Marítimo Nacional",
        "tipo": "museo",
        "lat": -33.03176,
        "lng": -71.63137,
        "horario": "Lunes a domingo de 10:00 a 18:00 horas.",
        "descripcion": "Importante espacio cultural emplazado en el histórico edificio de la Ex Escuela Naval en el cerro Artillería, dedicado a preservar y difundir la historia naval de Chile y las glorias de la Armada.",
        "fotos": ["maritimo-1.jpg"],
    },
]

# Zonas de precaución. Cada una es un círculo: un punto central y un radio en metros.
# Son un criterio del equipo y no garantizan seguridad.
ZONAS = [
    {"nombre": "Barrio Puerto", "centro": [-33.038324, -71.628372], "radio": 250},
    {"nombre": "Entorno del Terminal Rodoviario", "centro": [-33.046645, -71.606329], "radio": 200},
    {"nombre": "Calle Uruguay y Mercado Cardonal", "centro": [-33.045218, -71.607536], "radio": 120},
]

# Puntos de partida de ejemplo, para probar sin necesitar el GPS del computador.
PUNTOS_DE_PARTIDA = [
    {"nombre": "Plaza Sotomayor", "lat": -33.0376, "lng": -71.6277},
    {"nombre": "Cerro Alegre", "lat": -33.04342, "lng": -71.62985},
    {"nombre": "Terminal Rodoviario", "lat": -33.046645, "lng": -71.606329},
]
