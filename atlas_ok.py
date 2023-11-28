from qgis.core import QgsProject, QgsFeatureRequest
from PyQt5.QtCore import QSize
from Qgis2threejs.export import ThreeJSExporter
from Qgis2threejs.mapextent import MapExtent
import os

# Estilo
path_to_settings = 'C:/Users/ADMIN1/Desktop/WEB/4d/3d.qto3settings'

# Obtén el proyecto actual
project = QgsProject.instance()

# Nombres de las capas tg_lote y tg_construcciones
nombre_capa_lote = 'tg_lote'
nombre_capa_construcciones = 'tg_construcciones'

# Obtén las capas tg_lote y tg_construcciones
capa_lote = project.mapLayersByName(nombre_capa_lote)[0]
capa_construcciones = project.mapLayersByName(nombre_capa_construcciones)[0]

# Verifica si ambas capas existen
if capa_lote and capa_construcciones:

    # Obtiene todos los valores únicos de "id_lote" en la capa tg_lote
    valores_id_lote = capa_lote.uniqueValues(capa_lote.fields().indexFromName('id_lote'))

    # Itera sobre todos los valores únicos de "id_lote"
    for target_id_lote in valores_id_lote:

        # Filtra la capa tg_lote por el id_lote actual
        capa_lote.setSubsetString(f'"id_lote" = \'{target_id_lote}\'')
        # Refresca la capa tg_lote
        capa_lote.triggerRepaint()

        # Filtra la capa tg_construcciones por el id_lote actual
        capa_construcciones.setSubsetString(f'"id_lote" = \'{target_id_lote}\'')
        # Refresca la capa tg_construcciones
        capa_construcciones.triggerRepaint()

        # Realiza una solicitud para obtener la geometría correspondiente al id_lote actual en la capa tg_lote
        request = QgsFeatureRequest().setFilterExpression(f'"id_lote" = \'{target_id_lote}\'')
        features_lote = capa_lote.getFeatures(request)

        # Verifica si se encontró alguna geometría en la capa tg_lote
        if features_lote:
            # Obtén la primera geometría encontrada en la capa tg_lote (asumiendo que id_lote es único)
            feature_lote = next(features_lote)
            geometry_lote = feature_lote.geometry()

            # Centra el MapCanvas en la geometría del id_lote en la capa tg_lote
            iface.mapCanvas().setExtent(geometry_lote.boundingBox())

            # Refresca el MapCanvas
            iface.mapCanvas().refresh()
            # Realiza una solicitud para obtener la geometría correspondiente al id_lote actual en la capa tg_construcciones
            features_construcciones = capa_construcciones.getFeatures(request)

            # Verifica si se encontró alguna geometría en la capa tg_construcciones
            for feature_construcciones in features_construcciones:
                # Obtén la geometría encontrada en la capa tg_construcciones
                geometry_construcciones = feature_construcciones.geometry()

                # Configura las dimensiones de la textura
                TEX_WIDTH, TEX_HEIGHT = (1024, 1024)

                # Configura las opciones del mapa para el exportador ThreeJS
                mapSettings = iface.mapCanvas().mapSettings()
                MapExtent(geometry_construcciones.boundingBox().center(),
                          geometry_construcciones.boundingBox().width(),
                          geometry_construcciones.boundingBox().height(), 0).toMapSettings(mapSettings)

                # texture base size
                mapSettings.setOutputSize(QSize(TEX_WIDTH, TEX_HEIGHT))

                # Configura la carpeta de salida
                output_folder = f"C:/Program Files/Apache Software Foundation/Tomcat 8.5/webapps/3D/{target_id_lote}/"
                os.makedirs(output_folder, exist_ok=True)

                # Exporta la escena como página web en la carpeta correspondiente
                filename = f"{output_folder}index.html"

                exporter = ThreeJSExporter()
                exporter.loadSettings(path_to_settings)
                exporter.setMapSettings(mapSettings)

                # Exporta la escena
                success = exporter.export(filename)

                if success:
                    print(f"La exportación de la escena para id_lote {target_id_lote} fue exitosa en: {filename}")
                else:
                    print(f"Error al exportar la escena para id_lote {target_id_lote}.")

                # Break the loop after processing the first feature
                break
            else:
                print(f"No se encontraron geometrías para id_lote {target_id_lote} en la capa tg_construcciones.")
                continue  # Continue to the next iteration of the loop
