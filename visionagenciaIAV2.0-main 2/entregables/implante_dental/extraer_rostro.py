from pathlib import Path
import mediapipe as mp,json
root=Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/clientes/Vision Agencia/veneers_dental')
opts=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path='/tmp/face_landmarker.task'),num_faces=1,output_facial_transformation_matrixes=True)
with mp.tasks.vision.FaceLandmarker.create_from_options(opts) as detector:
 result=detector.detect(mp.Image.create_from_file(str(root/'last_frame_diente_faltante.png')))
 if not result.face_landmarks:raise RuntimeError('No face detected')
 points=[[p.x,p.y,p.z] for p in result.face_landmarks[0]]
 Path('entregables/implante_dental/rostro_assets/landmarks.json').write_text(json.dumps({'points':points,'matrix':result.facial_transformation_matrixes[0].tolist()}))
 print('landmarks',len(points))
 for i in [1,10,152,13,14,61,291,78,308,234,454]:print(i,points[i])
