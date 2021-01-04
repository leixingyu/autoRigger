# autoRigger
AutoRigger is a rig builder in Maya. It supports modular procedural rig building as well as providing pre-made template for Biped, Quadruped, and next up Bird.

quadruped rigging demo: https://youtu.be/GT15B_x8R9w

biped riggin demo: https://vimeo.com/372001985

modular rigging demo: https://vimeo.com/367496504

facial rigging demo: https://www.youtube.com/watch?v=Vnmq4ok0KUs

## Installation

1. Unzip to maya script directory

    (Example: C:/Users/Username/Documents/maya/[current maya version]/scripts/**autoRigger**)

    Or, unzip to custom directory, and add to PYTHONPATH system variable 
    
2. Install the maya-utility module in the same directory: https://github.com/sheldonlei/maya-utility

    (Example: C:/Users/Username/Documents/maya/[current maya version]/scripts/**utility**)

3. Execute the following command in script editor (python tab)
```python
from autoRigger import autoRigger
autoRigger.show()
```

## Current Version

<details>
  <summary>Update 1.1.2 (01/05/2021)</summary>
  <p>*updated code format to better adhere with PEP8</p>
</details>


## Past Updates

<details>
  <summary>Update 1.1.1 (09/20/2020)</summary>
  <p>*improved naming convention</p>
  <p>*updated user-interface
</details>

<details>
  <summary>Update 1.1.0 (04/08/2020)</summary>
  <p>*added quadruped template</p>
</details>

<details>
  <summary>Update 1.0.0 (11/08/2019)</summary>
  <p>*added biped template</p>
</details>

<details>
  <summary>Update 0.5.0 (10/19/2019)</summary>
  <p>*added modular system</p>
  <p>*updated new interface and functions</p>
</details>

<details>
  <summary>Update 0.4.0 (4/21/2019)</summary>
  <p>*integrated Body and Facial Rigging System</p>
  <p>*added Face Picker</p>
</details>

<details>
  <summary>Update 0.3.0 (3/24/2019)</summary>
  <p>*included Beta Facial Rigging System</p>
</details>

<details>
  <summary>Update 0.2.2 (3/22/2019)</summary>
  <p>*fixed IK/FK Arm bugs</p>
  <p>*updated Foot Roll and Foot Bank</p>
  <p>*included Flexible Spine Control</p>
</details>

<details>
  <summary>Update 0.2.1 (3/17/2019)</summary>
  <p>*fixed Bugs on Arm Result Joint</p>
</details>

<details>
  <summary>Update 0.2.0 (2/25/2019)</summary>
  <p>*now support Non-Tpose/Tpose Character Model</p>
  <p>*included IK/FK switch for Character arm</p>
  <p>*included Foot Bank attribute</p>
</details>

<details>
  <summary>Update 0.1.0 (12/29/2018)</summary>
  <p>*included adjustable spine and finger number</p>
  <p>*included one-click controller + constraint + default weightpaint</p>
  <p>*included Fore-arm twist and Foot roll</p>
</details>

