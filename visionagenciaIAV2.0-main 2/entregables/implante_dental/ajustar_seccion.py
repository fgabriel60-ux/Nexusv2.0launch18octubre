import bpy,os,traceback
old=bpy.context.window.scene;s=bpy.data.scenes['IMPLANTE_DENTAL_CINEMA']
try:
 bpy.context.window.scene=s
 # Shift the anatomical section behind the anterior half of the implant.
 inner=bpy.data.objects['DI_Maxilla_section'];old_anim=inner.animation_data.action if inner.animation_data else None
 oldmat=inner.data.materials[0]
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.045,2.10));new=bpy.context.object;new.scale=(5.47,.07,2.81);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);new.data.materials.append(oldmat)
 b=new.modifiers.new('Rounded section','BEVEL');b.width=.03;b.segments=3
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.29,depth=3.3,location=(0,0,1.75));c=bpy.context.object
 bpy.context.view_layer.objects.active=new;m=new.modifiers.new('Open canal','BOOLEAN');m.operation='DIFFERENCE';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
 bpy.data.objects.remove(inner,do_unlink=True);new.name='DI_Maxilla_section';new.animation_data_create();new.animation_data.action=old_anim
 # Clear the residual cortical front plane.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-1,2));c=bpy.context.object;c.scale=(6.5,2.16,4.5);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 slab=bpy.data.objects['DI_Maxilla_cortical'];bpy.context.view_layer.objects.active=slab;m=slab.modifiers.new('Front section clearance','BOOLEAN');m.operation='DIFFERENCE';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
 s.frame_set(570)
 path=os.path.expanduser('~/Desktop/IMPLANTE_DENTAL/IMPLANTE_DENTAL_CINEMA.blend');bpy.data.libraries.write(path,{s},fake_user=True,compress=True)
 responder({'ok':True,'saved':path})
except Exception:responder({'error':traceback.format_exc()});raise
finally:bpy.context.window.scene=old
