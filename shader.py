from OpenGL.GL import *
from OpenGL.GLUT import *
from random import random
import ctypes
import time
#Треугольники во весь экран

point_vertex1 = [[1.0, -1.0, 0.0], [1.0, 1.0, 0], [-1.0, -1.0, 0]]
point_vertex2 = [[-1.0, 1.0, 0.0], [-1.0, -1.0, 0], [1.0, 1.0, 0]]
xOrigin = 0.0
def specialkeys(button, state, x, y):
    global xOrigin
    iMouse = glGetUniformLocation(program, "iMouse")
    if button == GLUT_LEFT_BUTTON:
        if(state == GLUT_UP):
            glUniform2f(iMouse, x, y)
            xOrigin = -1.0
        else:
            xOrigin = x
def mouseMove(x, y):
    global xOrigin
    iMouse = glGetUniformLocation(program, "iMouse")
    if xOrigin >= 0.0:
        glUniform2f(iMouse, x, y)



def create_shader(shader_type, sourse):
    #empty_shader
    shader = glCreateShader(shader_type)
    #text -> shader_prog
    glShaderSource(shader, sourse)
    #compile_shder
    glCompileShader(shader)

    return shader
Time  = time.time()
def calc(x):
    global Time
    arg = time.time() - Time
    iTime = glGetUniformLocation(program, "iTime")
    glUniform1f(iTime, arg)
    glutTimerFunc(10, calc, 0)

def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, point_vertex1)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glVertexPointer(3, GL_FLOAT, 0, point_vertex2)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glDisableClientState(GL_VERTEX_ARRAY)
    glutSwapBuffers()


glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

glutInitWindowSize(1024, 1024)

glutInitWindowPosition(0, 0)

glutInit(sys.argv)

glutCreateWindow(b"ShaderWindow")

glutDisplayFunc(draw)

glutIdleFunc(draw)

glutMouseFunc(specialkeys)
glutMotionFunc(mouseMove)

glClearColor(0, 0, 0, 1)


vertex = create_shader(GL_VERTEX_SHADER, """

void main(){
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}""")

fragment = create_shader(GL_FRAGMENT_SHADER, """


uniform float iTime;
uniform vec2 iMouse;

float sdElipsoid(in vec3 pos, vec3 rad){

float k0 = length(pos/rad);
float k1 = length(pos/rad/rad);

    return k0* (k0-1.0)/k1;
}
float sdSphere(in vec3 pos, float rad){

    return length(pos) - rad;
}


float smin(float a, float b, float k){

    float h = max(k - abs(a-b), 0.0);
    return min(a,b) - h*h/(k * 4.0);
}
vec2 sdGuy(in vec3 pos){

    float t = 0.5;//fract(iTime); 
    
    float y = 4.0*t*(1.0 - t);
    
    float dy = 4.0*(1.0 - 2.0*t);
    
    vec2 u = normalize(vec2(1.0, -dy));
    
    vec2 v = vec2(dy, 1.0);
    
    vec3 cen = vec3(0.0, y, 0.0);
    
    float sy = 0.5 + 0.5*y;
    
    float sz = 1.0/sy;
    
    vec3 rad = vec3(0.25, 0.25*sy, 0.25*sz);
    
    vec3 q = pos - cen;
    
    //q.yz = vec2(dot(u, q.yz), dot(v, q.yz));
    
    float d = sdElipsoid(q,rad);
    
    vec3 h = q;
    //голова
    float d2 = sdElipsoid(h - vec3(0.0, 0.28, 0.0), vec3(0.2));
    float d3 = sdElipsoid(h - vec3(0.0, 0.28, -0.1), vec3(0.2));
 
    d2 = smin(d2,d3,0.03);
    d = smin(d, d2, 0.15);
    
    
    vec2 res = vec2(d, 2.0);
    //глаза
    vec3 sh = vec3( abs(h.x), h.yz );
    float d4 = sdSphere(sh - vec3(0.08,0.28,0.16), 0.05);
    
    if(d4 < d){
        res = vec2(d4, 3.0);
    }
    
    
    return res;


}
vec2 map(in vec3 pos){

    float d1 = sdGuy(pos);

    float d2 = pos.y - (-0.25);



    return min(d1, d2);
}

vec3 calcNormal(in vec3 pos){

    vec2 e = vec2(0.0001, 0.0);
    return normalize( vec3(
    map(pos + e.xyy).x-map(pos - e.xyy).x,
    map(pos + e.yxy).x-map(pos - e.yxy).x,
    map(pos + e.yyx).x-map(pos - e.yyx).x ) );
}

vec2 rayMarch(in vec3 ro, in vec3 rd){
    float m = -1.0;
    float t = 0.01;
    //ray march loop
    for(int i = 0; i < 100; i++) {
    
        vec3 pos = ro + t * rd;
        
        
        vec2 h = map(pos);
        m = h.y;
        if(h.x < 0.001){
            break;
        }
        t += h;
        if(t >20.0){
            break;
        }
        
    }
    if(t > 20.0){
        m = -1.0;
    }
    
    return vec2(t, m);

}
float random(vec2 ab)  {
	float f = (cos(dot(ab ,vec2(21.9898,78.233))) * 43758.5453);
	return fract(f);
}
float noise(in vec2 xy) 
{
	vec2 ij = floor(xy);
	vec2 uv = xy-ij;
	uv = uv*uv*(3.0-2.0*uv);
	

	float a = random(vec2(ij.x, ij.y ));
	float b = random(vec2(ij.x+1., ij.y));
	float c = random(vec2(ij.x, ij.y+1.));
	float d = random(vec2(ij.x+1., ij.y+1.));
	float k0 = a;
	float k1 = b-a;
	float k2 = c-a;
	float k3 = a-b-c+d;
	return (k0 + k1*uv.x + k2*uv.y + k3*uv.x*uv.y);
}


float castShadow(in vec3 ro, vec3 rd){
    
    float res = -1.0;
    float t = 0.001;
    for(int i = 0; i < 100; i++){
        vec3 pos = ro + t*rd;
        float h = map(pos).x;
        res = min(res, 16.0*h/t);
        if(res < 0.0001){
            break;
        }
        t += h;
        if (t>20.0){
            break;
        }
    }
    
    return res; 
    
}

void main()
{

    vec2 p = (2.0 * gl_FragCoord - vec2(600.0,600.0))/600.0; //получаем пиксель
    
    float an = 10 * iMouse.x/600; //iTime;
    
    
    vec3 ro = vec3(2.0*sin(an), 0.2, 2.0* cos(an)); //положение камеры
    
    
    
    vec3 ta = vec3(0.0, 0.75, 0.0); // target for camera
    
    
    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize( cross(ww, vec3(0,1,0)));
    vec3 vv = normalize( cross(uu, ww));
    
    
    
    vec3 rd = normalize(p.x*uu + p.y*vv + 1.5*ww); //-1.5 - глубина
    
    
    
    
    
    
    
    vec3 col = vec3(0.001, 0.001, 0.01) - 0.7*rd.y; //градиент на небе(оно не может быть однородным везде)
    
    col = mix (col, vec3(0.001,0.001, 0.07), exp(-30.0*rd.y)); // линия горизонта
    //Звезды
    float color = pow(noise(gl_FragCoord), 50.0) * 12.0;
        float r1 = noise((gl_FragCoord + vec2(sin(iTime), cos(iTime)) )*noise(vec2(sin(iTime*0.01))));
        float r2 = noise((gl_FragCoord + vec2(sin(iTime), cos(iTime)) )*noise(vec2(cos(iTime*0.01), sin(iTime*0.01))));
        float r3 = noise((gl_FragCoord + vec2(sin(iTime), cos(iTime)) )*noise(vec2(cos(iTime*0.05))));
    col += vec3(color*r1, color*r2, color*r3);
    
    vec2 tm = rayMarch(ro, rd);
    
    
    if(tm.y > 0.0){
    
    float t = tm.x;
    vec3 pos = ro + t * rd;
    vec3 nor = calcNormal(pos);
    
    vec3 mate = vec3(0.3);
    
    vec3 sun_dir = normalize(vec3(0.5, 0.5, 0.5) );
    float sun_dif = clamp( dot (nor, sun_dir), 0.0, 0.1);
    float sun_shadow = step(castShadow(pos + 0.001*nor, sun_dir),0.0);
    float sky_dif = clamp( 0.5 + dot (nor, vec3(0.0,1.0,0.0)), 0.0, 1.0); //0.5 + чтобы сдеелать более мягкую растушевку
    float bounce_dif = clamp( 0.5 + dot (nor, vec3(0.0,-1.0,0.0)), 0.0, 1.0); // тот же свет что и от неба только снизу координата -1
    
    col = mate * vec3(10.0, 10.5, 10.0) * sun_dif * sun_shadow;
    
    col += mate * vec3(0.0, 0.0, 0.0) * sky_dif;
    
    col += mate * vec3(1.0, 1.0, 1.0) * bounce_dif;
    }
    
    col = pow(col, vec3(0.4545));
    
    gl_FragColor = vec4(col,1.0);
}""")

program = glCreateProgram()
glAttachShader(program, vertex)
glAttachShader(program, fragment)

glLinkProgram(program)
glUseProgram(program)



# Определяем массив цветов (по одному цвету для каждой вершины)

glutTimerFunc(10, calc, 0)
glutMainLoop()









