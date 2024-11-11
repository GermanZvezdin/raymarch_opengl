# Трассировка лучей Звездин Герман 305 группа


## Порядок установки:

- На компьютере должна быть Visual Studio

- В папке Exam\python_installer лежит установщик python-3.9.0-amd64.exe его нужно запустить от имени администратора и поставить галочку Add Python to PATH

- После установки python-3.9.0-amd64.exe в той же папке лежит файл pip_installer.bat его нужно запустить от имени администратора. ОС может запретить Вам его запускать, это нужно пригнорироватьи и нажать на выполнить  в любом случае.

- В папке Exam выполните либо instal_module_x32.bat - если у Вас 32-разрядная ОС, либо  instal_module_x64.bat - усли у Вас 64-разрядная ОС. 

При запуске скриптов может возникнуть ошибка аналогичная пункту 3) 

- Чтобы запустить первую сцену используйте скрипт run_scene1.bat.

- Чтобы запустить вторую сцену используйте скрипт run_scene2.bat 
При запуске скриптов может возникнуть ошибка аналогичная пункту 3) 


## Описание эффектов:

### Сцена 1: 

- Отбрасывание тени на другие объекты

- Зеркальные грани 

- Антиалисинг(по умолчанию выключен т.к очень сильно падает FPS описан в отдельной функции в фрагментном шейдере AntiA) 

- объекты с изменением связности (фиолетовые сферы и октаэдер) 

- CSG объект - зеленый октаэдер со сферой и кубом. 

- Нечетки тени 

- Нетривиальная модель освещения Ambient occlusion

- Освещение по Фонгу фиолетового объекта

- Пост-эффект по нажатию на стрелку вверх(объемный туман). Стрекла вниз - выключение. 

<img width="599" alt="Снимок экрана 2021-02-13 в 13 45 58" src="https://user-images.githubusercontent.com/71877725/107848215-9ee91f00-6e02-11eb-9930-74593b25c8ec.png">

### Сцена 2: 

- Полигональный источник освещения. 
- Нечеткие отражения

![capture (4)](https://user-images.githubusercontent.com/71877725/107848205-909b0300-6e02-11eb-9c1c-2753c01fd920.gif)

Исходный код сцен лежит в Exam/scene

# English version 

# Ray tracing Zvezdin German 305 group


## Installation procedure:

- The computer must have Visual Studio installed

- The installer is located in the Exam\python_installer folder python-3.9.0-amd64.exe you need to run it as an administrator and check the Add Python to PATH box

- After installation python-3.9.0-amd64.exe in the same folder is the pip_installer file.bat you need to run it as an administrator. The OS can prevent you from running it, you need to ignore it and click on run anyway.

- In the Exam folder, run either install_module_x32.bat - if you have a 32-bit OS, or install_module_x64. bat-if you have a 64-bit OS.

When running scripts, an error similar to step 3 may occur)

- To start the first scene, use the run_scene1.bat script.

- To start the second scene, use the run_scene2 script.bat
When running scripts, an error similar to step 3 may occur)


## Description of the effects:

### Scene 1:

- Casting shadows on other objects

- Mirror faces

- Anti-aliasing(disabled by default because the FPS drops very much is described in a separate function in the Antia fragment shader)

- objects with a change in connectivity (purple spheres and octahedron)

- CSG object - green octahedron with sphere and cube.

- Fuzzy shadows

- Non-trivial Ambient occlusion lighting model

- Lighting by the Phong of the purple object

- Post-effect by clicking on the up arrow (volumetric fog). Have Strela down and off.

<img width="599" alt="Снимок экрана 2021-02-13 в 13 45 58" src="https://user-images.githubusercontent.com/71877725/107848215-9ee91f00-6e02-11eb-9930-74593b25c8ec.png">

### Scene 2:

- Polygonal light source.
- Fuzzy reflections

![capture (4)](https://user-images.githubusercontent.com/71877725/107848205-909b0300-6e02-11eb-9c1c-2753c01fd920.gif)

The source code of the scenes is in Exam/scene

