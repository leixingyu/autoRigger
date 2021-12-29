<div align="center">
<h1 align="center">AutoRigger 2.0</h1>

  <p align="center">
    AutoRigger is an automated rig builder used in Maya. It currently supports procedural
rigging based on modules as well as pre-made template for biped, quadruped and chain.
    <br />
    <a href="https://youtu.be/893BSzy3lCs">Chain Demo</a>
    |
    <a href="https://youtu.be/GT15B_x8R9w">Quadruped Demo</a>
    |
    <a href="https://youtu.be/tMrX3lT2Iy8">Biped Demo</a>
  </p>
</div>


## About The Project

<center>
<img align="center" src="https://i.imgur.com/9E5V0Rn.png" alt="autoRigger" height="280px"/>
</center>

The AutoRigger tool started out as my practice for maya scripting back in late 2018. 
But Little by little,
I started to implement new rigging knowledge on to it. After years
of expansion, it became my rigging tool kit which handles a lot of the automation
in general rigging process.

## Getting Started

1. Unzip the **auto-rigger** package under
`%USERPROFILE%/Documents/maya/[current maya version]/scripts/`
or a custom directory under `PYTHONPATH` env variable. 

2. Rename the package to something like `autoRigger`

3. Launch through script editor:
    ```python
    from autoRigger import autoRigger
    autoRigger.show()
    ```

## Usage

The autoRigger is modular and very straight forward to use; Each item on the left is referred as a rig object, you create them in the scene
individually and piece together to build the final rig; there are also
pre-made template for standard characters like biped and quadruped.

**Create Guide**
<img align="right" src="https://i.imgur.com/Gi6GMUT.png" alt="interface" height="320px" style="margin: 40px 10px"/>

- choose a rig object, and then enter specific properties on the right-side field, finally click guide.

- this creates a guided locators or the rough joint placement of the rig.
you are now free to move, rotate, scale the locators around to better match the
target mesh.

**Build Rig**

- when you are satisfied with the guide placement, click build. it will
generate all the joints, controllers and constraints. 
- The next step if for you to skin your character/creature using anything you
prefer 
- note: autoRigger isn't a skinning tool

## Scripting API

>Anything GUI can do, scripting can do better;

the rig object and all of its components can be accessed through scripting 
with ease, as each rig object is a class inheriting the abstract bone class.

### Example:
To instantiate a rig object, build guide and rig
```python
from autoRigger.constant import Side
from autoRigger.chain import chainEP

test_chain = chainEP.ChainEP(
   name='rope',
   side=Side.LEFT,
   segment=20,
   curve='curve1',
   cv=10
)

test_chain.build_guide()
test_chain.build_rig()
```

Access rig object properties:

```
>>> test_chain.name
output: rope
```

```
>>> test_chain.side
output: Side.LEFT
```

```
>>> test_chain.type
output: chain
```

```
>>> test_chain.scale
output: 1
```
```
>>> test_chain.components

# this is used mostly in template such as biped or quadruped
# which will yield all rig sub-components
output: []
```

Access rig object nodes in maya scene

```python
# shared maya nodes
jnts = test_chain.jnts
root_jnt = jnts[0]
top_jnt = jnts[-1]

"""
subsequently:
['chain_l_rope0_jnt']
['chain_l_rope19_jnt']
"""

ctrls = test_chain.ctrls
locators = test_chain.locs
offset_group = test_chain.offsets

# chain specific maya nodes
test_chain.clusters
test_chain.guide_curve
test_chain.curve
test_chain.cvs
```


## Roadmap

- [ ] integrate facial rigging
- [ ] bird template
- [ ] vehicle template
- [ ] refactor quadruped leg modules

## Versions
<details>
  <summary>Update 2.0 (current)</summary>
    <ul>
      <li>rig object abstraction</li>
      <li>added chain modular rigging package</li>
      <li>added dynamic property widget</li>
    </ul>
</details>

<details>
  <summary>Update 1.2 (01/05/2021)</summary>
    <ul>
      <li>PEP8 code re-formatting</li>
      <li>updated naming convention</li>
      <li>updated user-interface</li>
    </ul>
</details>

<details>
  <summary>Update 1.1 (04/08/2020)</summary>
    <ul>
      <li>added quadruped template rigging</li>
      <li>added biped template rigging</li>
    </ul>
</details>

<details>
  <summary>Update 1.0 (10/19/2019)</summary>
    <ul>
      <li>re-built autoRigger as a modular rig system</li>
      <li>updated user-interface</li>
    </ul>
</details>

<details>
  <summary>Update 0.4 (04/21/2019)</summary>
    <ul>
      <li>integrated body and face rigging</li>
      <li>added face picker</li>
    </ul>
</details>

<details>
  <summary>Update 0.2 (03/22/2019)</summary>
    <ul>
      <li>added FK/IK to limb</li>
      <li>added flexible spine control</li>
    </ul>
</details>

<details>
  <summary>Update 0.1 (12/29/2018)</summary>
    <ul>
      <li>initial release of the autoRigger tool</li>
      <li>included one-click rig building</li>
      <li>included default skin binding</li>
    </ul>
</details>
