# Under Construction

Looking back at this project I started three years ago, I realized there's a huge
room for improvement as my skill grows. So, I decided to do a major overhaul. It may take couple of weeks or 
months, maybe even years. who knows?

#### Current Status

- [x] code refactor (including rig abstraction)
- [x] directory organization
- [x] variable naming change
- [x] formatting (imports, line length, docstring etc)
- [x] data widget mapping
- [ ] testing

#### Future Status

- [ ] implement facial rigging
- [ ] future refactor quadruped leg modules
- [ ] to-dos

## Introduction

AutoRigger is a rig builder in Maya. It supports modular procedural rig building as well
as providing pre-made template for Biped, Quadruped, and next up Bird or Vehicle and more...

- [Quadruped Rigging Demo](https://youtu.be/GT15B_x8R9w)
- [Biped Rigging Demo](https://vimeo.com/372001985)
- [Modular Rigging Demo](https://vimeo.com/367496504)
- [Facial Rigging Demo](https://www.youtube.com/watch?v=Vnmq4ok0KUs)

## Installation

Install the auto-rigger and [maya-utility](https://github.com/leixingyu/maya-utility) under
`C:/Users/Username/Documents/maya/[current maya version]/scripts/`

or unzip to your custom directory, and add to PYTHONPATH system variable 

Launch:
```python
from autoRigger import autoRigger
autoRigger.show()
```

![gugu](https://i.imgur.com/9E5V0Rn.png)

### Release Version

<details>
  <summary>Update 1.1.2 (01/05/2021)</summary>
  <p>*updated code format to better adhere with PEP8</p>
  <p>*improved naming convention</p>
  <p>*updated user-interface
</details>

### Past Updates

<details>
  <summary>Update 1.1.0 (04/08/2020)</summary>
  <p>*added quadruped template</p>
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
  <summary>Update 0.2.2 (3/22/2019)</summary>
  <p>*IK/FK Arm</p>
  <p>*Foot Roll and Foot Bank</p>
  <p>*Flexible Spine Control</p>
</details>

<details>
  <summary>Update 0.1.0 (12/29/2018)</summary>
  <p>*included adjustable spine and finger number</p>
  <p>*included one-click controller + constraint + default weightpaint</p>
  <p>*included Fore-arm twist and Foot roll</p>
</details>

