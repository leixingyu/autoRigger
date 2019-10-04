# autoRigger-Human
AutoRigger-Human is an auto rigging tool for maya, specifically designed for create fast and functional rigs for human characters

face rig video demo (1.4 version): https://www.youtube.com/watch?v=Vnmq4ok0KUs

body rig video demo (1.0 version): https://vimeo.com/308809558

## Installation
create a folder called AutoRigger in your maya system path

example: C:\Users\Username\Documents\maya\2018(current maya version)\scripts\autoRigger

place all .py files in your folder


Enter following command in maya script editor(python tab)
```python
from autoRiggerPlus import interface
reload(interface)
```

## Future Development
currently working on modular rigging system implementation

## Past Updates

<details>
  <summary>Update 1.4 (4/21/2019)</summary>
  <p>*Integrated Body and Facial Rigging System</p>
  <p>*Added Face Picker</p>
</details>

<details>
  <summary>Update 1.3 (3/24/2019)</summary>
  <p>*Included Beta Facial Rigging System</p>
</details>

<details>
  <summary>Update 1.2 (3/22/2019)</summary>
  <p>*Fixed IK/FK Arm bugs</p>
  <p>*Updated Foot Roll and Foot Bank</p>
  <p>*Included Flexible Spine Control</p>
</details>

<details>
  <summary>Update 1.12 (3/17/2019)</summary>
  <p>*Fixed Bugs on Arm Result Joint</p>
</details>

<details>
  <summary>Update 1.1 (2/25/2019)</summary>
  <p>*Now support Non-Tpose/Tpose Character Model</p>
  <p>*Included IK/FK switch for Character arm</p>
  <p>*Included Foot Bank attribute</p>
</details>

<details>
  <summary>Update 1.0 (12/29/2018)</summary>
  <p>*Included adjustable spine and finger number</p>
  <p>*Included one-click controller + constraint + default weightpaint</p>
  <p>*Included Fore-arm twist and Foot roll</p>
</details>

