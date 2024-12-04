import numpy as np
from scipy.spatial.transform import Rotation as R
from sklearn.cluster import DBSCAN
import os

# Función para convertir una pose (traslación + quaternion) a una matriz 4x4
def pose_to_matrix(translation, quaternion):
    rotation_matrix = R.from_quat(quaternion).as_matrix()
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = translation
    return transformation_matrix

# Función para proyectar coordenadas 2D a 3D
def project_to_3d(x, y, depth, K, pose_matrix):
    K_inv = np.linalg.inv(K)
    pixel_coords = np.array([x, y, 1]).reshape((3, 1)).astype(float)
    camera_coords = K_inv @ pixel_coords * depth
    camera_coords = np.vstack((camera_coords, [1]))
    world_coords = pose_matrix @ camera_coords
    return world_coords[:3].flatten()

# Función de Non-Maximum Suppression (NMS) para esferas 3D
def nms_3d_spheres(spheres, threshold=0.5):
    if len(spheres) == 0:
        return []

    # Convertir a array de numpy
    spheres = np.array(spheres)
    
    # Aplicar clustering para identificar grupos de esferas cercanas
    clustering = DBSCAN(eps=threshold, min_samples=1).fit(spheres)
    labels = clustering.labels_

    # Lista para guardar las esferas seleccionadas
    selected_spheres = []

# Aplicar NMS en cada grupo de esferas
    for label in np.unique(labels):
        group = spheres[labels == label]
        centroid = np.mean(group, axis=0)
        distances = np.linalg.norm(group - centroid, axis=1)
        min_distance_index = np.argmin(distances)
        selected_spheres.append(group[min_distance_index])
        
    return selected_spheres

# Cargar datos de detecciones
detections = np.load('tmp/poses_and_coordinates.npz')
frames = detections['frames']
xs = detections['xs'].astype(float)
ys = detections['ys'].astype(float)
poses = detections['poses']
intrinsics = np.load('tmp/reconstructions/intrinsics.npy')

# Obtener los intrínsecos de la cámara
fx, fy, cx, cy = intrinsics[0] * 10

# Crear una matriz intrínseca K
K = np.array([[fx, 0, cx],
              [0, fy, cy],
              [0, 0, 1]])

# Suponiendo una profundidad media (puedes ajustar esto según tu caso)
depth = 1.0

# Función para crear una esfera de puntos
def create_sphere(center, radius=0.2, resolution=20):
    points = []
    for i in range(resolution):
        lat = np.pi * (-0.5 + float(i) / (resolution - 1))
        for j in range(resolution):
            lon = 2 * np.pi * float(j) / (resolution - 1)
            x = center[0] + radius * np.cos(lat) * np.cos(lon)
            y = center[1] + radius * np.cos(lat) * np.sin(lon)
            z = center[2] + radius * np.sin(lat)
            points.append([x, y, z])
    return points

# Proyectar todas las detecciones a coordenadas 3D
points_3d = []
for i in range(len(frames)):
    pose_matrix = pose_to_matrix(poses[i][:3], poses[i][3:])  # Convertir pose a matriz 4x4
    x = xs[i]
    y = ys[i]
    point_3d = project_to_3d(x, y, depth, K, pose_matrix)
    points_3d.append(point_3d)

# Aplicar NMS para eliminar esferas redundantes
points_3d = nms_3d_spheres(points_3d, threshold=0.5)

# Crear esferas en las posiciones 3D detectadas
sphere_points = []
for point in points_3d:
    sphere_points.extend(create_sphere(point))

# Definir el directorio de resultados
output_dir = 'tmp/results'

# Escribir los puntos de las esferas en un archivo PLY
output_file_path = os.path.join(output_dir, 'spheres.ply')
with open(output_file_path, 'w') as f:
    f.write("ply\n")
    f.write("format ascii 1.0\n")
    f.write(f"element vertex {len(sphere_points)}\n")
    f.write("property float x\n")
    f.write("property float y\n")
    f.write("property float z\n")
    f.write("end_header\n")
    for sp in sphere_points:
        f.write(f"{sp[0]} {sp[1]} {sp[2]}\n")

print("Archivo spheres.ply creado con éxito.")