import Physics_engine2 as pe

pygame = pe.pygame
cuboid = pe.cuboid
entity = pe.collidable_object

class constant:

    fireball_power = 0.175

fireball_count = 0
fireballs = []
def tick(e):
    global fireballs,fireball_count
    keys = e[0]
    events = e[1]
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            fireballs.append(entity("fireball"+str(fireball_count),pe.player.x,pe.player.y-0.2,pe.player.z,0.2,0.1,0.5,point="fireball.png",lines=False,friction=0.8,vol=(constant.fireball_power * pe.sin(pe.player.ry*pe.pi/180)* pe.cos(-pe.player.rx*pe.pi/180),constant.fireball_power*pe.sin(-pe.player.rx*pe.pi/180),-constant.fireball_power* pe.cos(-pe.player.rx*pe.pi/180) * pe.cos(pe.player.ry*pe.pi/180))))
            fireball_count += 1

    if pe.player.y <= -20:
        pe.player.x = 0
        pe.player.z = 0
        pe.player.y = 3

    for fireball in fireballs[:]:#fireballs[:] needed as origenal fireballs may be edited inside loop
        if abs(fireball.vx) + abs(fireball.vz) < 0.0001:
            fireballs.remove(fireball)
            fireball.destroy()
    


pe.tick = tick


#Notes on usage: (written 2020 -- i.e. a few years after origenal code)

#coord_mylt   - is the number of times an image should repeat on all faces
#auto_scaling - will deal with non-square faces for you with the number
#               meaning how manny times the texture should repeat on the
#               smallest length.
#



cuboid(-20,0,-20,20,1,20,{"top":"metal_plating.png"},coord_mylt = 10)
cuboid(-2,8,-2,2,12,2,"metal_plating.png",coord_mylt = 6)
cuboid(-22,1,-4,-18,2,4,"metal_plating.png",auto_scaling={"fb":0.25,"lr":0.25,"tb":1})
cuboid(-23,1,-2,-28,6,4,"metal_plating.png",auto_scaling={"fb":1.25,"lr":1.5,"tb":1.25})
cuboid(-24,2,-4,-25,3,-2,"metal_plating.png",auto_scaling={"fb":0.25,"lr":0.25,"tb":0.25})
cuboid(-27,3,-4,-28,4,-2,"metal_plating.png",auto_scaling={"fb":0.25,"lr":0.25,"tb":0.25})
cuboid(-30,4,-6,-36,5,6,"metal_plating.png",auto_scaling={"fb":0.25,"lr":0.25,"tb":1.5})


pe.Start()
