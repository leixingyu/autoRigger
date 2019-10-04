from autoRiggerPlus import base, finger, hand, limb

reload(finger)
reload(hand)
reload(limb)

# testing limb
arm = limb.Limb(prefix='test', side='R', id='leg')
arm.setArmLeg('Leg')
arm.buildGuide()
arm.constructJnt()
arm.placeCtrl()
arm.deleteShape()
arm.deleteGuide()
arm.addConstraint()


# testing finger
'''
indexFinger = finger.Finger(prefix='test', side='R', id='index')
indexFinger.buildGuide()
indexFinger.buildRig()
'''

# testing hand
'''
leftH = hand.Hand(prefix='test', side='L', id='aleftHand')
leftH.setLocAttr(startPos=[5, 0, 0])
leftH.buildGuide()
leftH.buildRig()
'''
