from OpenGL.GL import *
from OpenGL.GLUT import *
from random import random
import ctypes
import time

# Треугольники во весь экран

point_vertex1 = [[1.0, -1.0, 0.0], [1.0, 1.0, 0], [-1.0, -1.0, 0]]
point_vertex2 = [[-1.0, 1.0, 0.0], [-1.0, -1.0, 0], [1.0, 1.0, 0]]
xOrigin = 0.0

def specialkeys2(key, x, y):

    if key == GLUT_KEY_UP:
        fog_on = glGetUniformLocation(program, "flag")
        glUniform1f(fog_on, 10.0)
    if key == GLUT_KEY_DOWN:
        fog_off = glGetUniformLocation(program, "flag")
        glUniform1f(fog_off, -10.0)

def specialkeys(button, state, x, y):
    global xOrigin
    iMouse = glGetUniformLocation(program, "iMouse")
    if button == GLUT_LEFT_BUTTON:
        if (state == GLUT_UP):
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
    # empty_shader
    shader = glCreateShader(shader_type)
    # text -> shader_prog
    glShaderSource(shader, sourse)
    # compile_shder
    glCompileShader(shader)

    return shader


Time = time.time()


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

glutInitWindowSize(512, 512)

glutInitWindowPosition(0, 0)

glutInit(sys.argv)

glutCreateWindow(b"ShaderWindow")

glutDisplayFunc(draw)

glutIdleFunc(draw)
glutSpecialFunc(specialkeys2)
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
uniform vec2 iResolution;
uniform float flag;



const float FAR_INF = 1e10;
const float EPS = 1e-3;
const float PI = 3.14159265359;
vec2 Hash2(uint n) 
{
	n = (n << 13U) ^ n;
    n = n * (n * n * 15731U + 789221U) + 1376312589U;
    uvec2 k = n * uvec2(n,n*16807U);
    return vec2( k & uvec2(0x7fffffffU))/float(0x7fffffff);
}



float rand (vec2 st) {
    return fract(sin(dot(st.xy,
                         vec2(12.9898,78.233)))*
        43758.5453123);
}

vec3 rand3(vec3 st) {
    
 	return normalize(vec3(Hash2(uint(st.x)), rand(st.yz)));    
    
}

float sph(in vec3 pos, in vec3 cen, in float r){
	return length(pos - cen) - r; 
}

float plane(in vec3 pos, in float r){

	return pos.y - (-r);
}

vec2 mmax(in vec2 a, in vec2 b){
	
	return a.x > b.x ? a: b;
}

vec2 mmin(in vec2 a, in vec2 b){
	
	return a.x < b.x ? a: b;
}

float smin( float d1, float d2, float k ) {

    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    
    return mix( d2, d1, h ) - k*h*(1.0-h); 
    
}

float smax( float d1, float d2, float k ) {
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h); 
}

float sint( float d1, float d2, float k ) {
    float h = clamp( 0.5 - 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) + k*h*(1.0-h); 
}

float Oct(vec3 pos, vec3 cen){
    float s = 0.5;
    pos = abs(pos - cen);
    return (pos.x+pos.y+pos.z-s)*0.57735027;
}
float box( vec3 pos, vec3 center, vec3 size, float corner )
{
    return length( max( abs( pos-center )-size, 0.0 ) )-corner;
}

float sdNotTrivialMorph(in vec3 pos){
    float k = 0.1;//abs(sin(iTime/100.0));
    float disp = sin(5.0*pos.x) * sin(5.0*pos.y) * sin(5.0*pos.z) * 0.15;
    
    float f1 = sph(pos, vec3(0.5*sin(iTime) + 2.5*sin(iTime/3.0),2.0 + abs(sin(iTime)) -1.0, 0.5*cos(iTime)+2.5*cos(iTime/3.0)), 0.5); 
    
    float f2 = sph(pos, vec3(2.5*sin(iTime/3.0)   ,2.5-1.0,   2.5*cos(iTime/3.0)), 0.7); 
    float f3 = sph(pos, vec3(0.5*sin(iTime) + 2.5*sin(iTime/3.0),0.5*cos(iTime)+2.5 -1.0,2.5*cos(iTime/3.0)), 0.5);
    float f4 = Oct(pos, vec3(2.5*sin(iTime/2.0)   ,2.5-1.0,   2.5*cos(iTime/2.0) ));
    
    
    float res = smin(f1 +sin(disp), f2+cos(disp), k); 
    res = smin(res, f3+disp, k);
    res = smin(res, f4 +0.1*disp, k);
    return res; 
    
}
float CSGSD(in vec3 pos){
    
    float k = 0.5; 
    
    float f1 = Oct(pos, vec3(4.0 * sin(iTime), 2.0 * abs(cos(iTime)), 4.0*cos(iTime)) );
    float f2 = sph(pos, vec3(4.0 * sin(iTime), 2.0 *  abs(cos(iTime)),4.0* cos(iTime)), 1.0 * abs(sin(iTime)) );
    float f3 = box(pos, vec3(4.0 * sin(iTime), 2.0 * abs(cos(iTime)), 4.0*cos(iTime)), vec3(0.5), 0.0);
    
    return smin(f1, smax(f2, f3, k), k);

}
vec2 map(in vec3 pos){
    
    //float disp = 
	vec2 d = vec2(sph(pos, vec3(0.0), 1.5), 1.0);
    vec2 d1 = vec2(sph(pos, vec3(-3.0*sin(iTime), 0.3-0.31-sin(iTime*5.0), 3.0*cos(iTime)), 0.5), 2.0);
    vec2 d2 = vec2 (plane(pos, 1.5), 3.0);
    vec2 d3 = vec2(sph(pos, vec3(3.0*cos(iTime), -1.0, 3.0*sin(iTime)), 0.50),4.0);
    
    
    vec2 d5 = vec2(sdNotTrivialMorph(pos), 6.0);
    
    //vec2 d5 = vec2(sph(pos, vec3(-0.5, 0.0, 5.0), 1.5), 6.0);
    vec2 res = mmin(mmin(d, mmin(d1,d2)), d3);
    
    
    
    vec2 d6 = vec2(CSGSD(pos), 7.0);
    res = mmin(res, d5);
    res = mmin(res, d6);
    return res;
}


vec2 ray_cast(in vec3 ro, in vec3 rd){

	float t = 0.0; 
    float d = 0.0; 
    float absSum = 1.0;
    for(int i = 0; i < 10000; i++){
    	vec2 pos = map(ro + t* rd); 
        
        if(pos.x < 0.0001){
        	
        	pos.x = t; 
           	
            return pos;
        } 
        
        if(pos.x > 200.0){
        	break;
        }
        
        t += pos.x*0.5;
    }
    
    return vec2(-1.0);
}
vec3 normal(in vec3 pos){

	const vec3 eps = vec3(0.001, 0.0, 0.0);
    
    
    
    float grad_x = map(pos + eps.xyy).x - map(pos - eps.xyy).x;
    float grad_y = map(pos + eps.yxy).x - map(pos - eps.yxy).x;
    float grad_z = map(pos + eps.yyx).x - map(pos - eps.yyx).x;
    
    
    
    return normalize(vec3(grad_x, grad_y, grad_z));



}

float calcAO( in vec3 pos, in vec3 nor ){
	float occ = 0.0;
    float sca = 1.0;
    for( int i=0; i<5; i++ )
    {
        float h = 0.01 + 0.12*float(i)/4.0;
        float d = map( pos + h*nor ).x;
        occ += (h-d)*sca;
        sca *= 0.95;
        if( occ>0.35 ) break;
    }
    return clamp( 1.0 - 3.0*occ, 0.0, 1.0 ) * (0.5+0.5*nor.y);
}


float checkers( in vec3 p ) {
    vec3 s = sign(fract(p*0.5)-0.6);
    return 0.5 - 0.5*s.x*s.y*s.z;
}

float diffuse_light(in vec3 pos, in vec3 cen){
    
	vec3 nor = normal(pos);
    vec3 dir_to_light = normalize(cen-pos);
    float diff_intens = dot(nor, dir_to_light);
    
    return diff_intens;

}
float phong_light(in vec3 pos, in vec3 cen, in vec3 ro, in float k){
	
    float specPower = k;
    vec3 n = normal(pos);
    vec3 l = normalize(cen-pos);
    vec3 v = normalize(ro-pos);
    vec3 r = reflect(v, n);
    float phong_light = pow ( max ( dot ( l, r ), 0.0 ), specPower );
    return phong_light;

}
float fog(in vec3 pos) {
	
    float ans = 1.0;
    if(abs(pos.x) > 10.0) ans *= 1.0 / (pos.x*pos.x*0.01);
    //if(abs(pos.y) > 10.0) ans *= 1.0 / (pos.y*pos.y*0.01);
    if(abs(pos.z) > 10.0 ) ans *= 1.0 / (pos.z*pos.z*0.01);
    
    return ans;

}


float shadow(vec3 pos, vec3 lightpos){
	vec3 rd = normalize(lightpos-pos);
    float res = 1.0;
    float t = 0.0;
    
    for (float i = 0.0; i < 1000.0; i++)
    {
		vec2 h = map(pos + rd * t);
        res = min(res, 15.0 * h.x / t);
        t += h.x;
        
        if ((res < 0.000001 || t > 3200.0)) break;
        
    }
    
    return clamp(res, 0.0, 1.0);
    
}

float BeerLambert(float absorptionCoefficient, float distanceTraveled) {
    return exp(-absorptionCoefficient * distanceTraveled);
}

float volume_dist(in vec3 pos){
    vec3 volume_pos = vec3(0.0, 1.5, 0.0); 
    
    float volume_rad = 9.0; 
    
    return length(pos - volume_pos) - volume_rad;
    
}
float fogDensity(vec3 currentPos, float sdf) {
    
    vec3 SPHERE_POS = vec3(0.0, 1.5, 0.0);
    vec3 localCurrentPos = currentPos - SPHERE_POS;
    vec2 rotate1 = vec2(cos(iTime), -sin(iTime));
    vec2 rotate2 = vec2(sin(iTime), cos(iTime));
    localCurrentPos.xz = vec2(dot(rotate1, localCurrentPos.xz), dot(rotate2, localCurrentPos.xz));
    float density = rand(localCurrentPos.xz);
    return min(density, -sdf);
}
vec4 volFog(in vec3 ro, in vec3 rd) {
    
    const float march_size = 0.1; 
    const int max_steps = 100; 
    
    
    
    float absorption = 0.2;
    float opacity = 1.0;
    vec3 fogEffect = vec3(0.0);
    for(int i = 0; i < max_steps; i++){
        
        vec3 cur_pos = ro + rd * march_size * float(i); 
        
        if(volume_dist(cur_pos) < 0.0) {
            float prevOpacity = opacity;
            opacity *= BeerLambert(absorption * fogDensity(cur_pos, volume_dist(cur_pos)), march_size); 
            float abss = prevOpacity - opacity;
            
            fogEffect += vec3(abss);
        }
    
    }
    
    return vec4(fogEffect, opacity);

}

vec3 mirror(in vec3 opos, in vec3 ord) {
    
    
    vec3 n = normal(opos);
    vec3 ro = opos;
    vec3 rd = n;
    int max_step =1;
    vec3 lp = vec3(5.0, 5.0,0.0);
    vec3 col =vec3(1.0,1.0,1.0);
    for(int i=0; i < max_step; i++){
        vec2 h = ray_cast(ro+0.1*n, reflect(-ro, n));


        if(h.x > -1.0) {
            vec3 pos = ro + h.x *rd;
         
            if(h.y == 2.0){
                col = vec3(0.0, 0.0, 1.0) * calcAO(pos, normal(pos));
                col *= shadow(pos, lp);
                col *= 2.0;
                
            }


            if(h.y == 3.0) {

                col = vec3(0.7, 0.7, 0.7) * calcAO(pos, normal(pos));
                

                col += checkers(pos);
                col *= mix(col, vec3(0.9), 20.0);
                col *= shadow(pos, lp);

            }
            if(h.y == 4.0) {

                col = vec3(1.0,0.0,0.0) * calcAO(pos, normal(pos));
                col *= shadow(pos, lp);
                col *= 1.5;



            }
            
            if(h.y == 6.0) {
                col = vec3(1.0,0.0,0.7) * calcAO(pos, normal(pos));
                col *= shadow(pos, lp);
                col += phong_light(pos, -lp, ro, 2000.0);
            }
            //col *= 2.0;
            
            if(h.y == 7.0) {
                col = vec3(0.0,1.0,0.7) * calcAO(pos, normal(pos));
                col *= shadow(pos, lp);
                col += phong_light(pos, -lp, ro, 2000.0);
                
            }
            col *= fog(pos);
            //col = vec3(h.y,0,0);
        }else {
             col = vec3(0.7, 1.0, 1.5)*exp(-rd.y);
    }
    }
    
    
    return col;
    
    
    
}
vec4 render(in vec3 ro, in vec3 rd){
    
    vec2 h = ray_cast(ro, rd);
    vec3 lp = vec3(5.0, 5.0,0.0);
    vec3 mp = vec3(0.0);
    vec3 col = vec3(1.0,1.0,1.0);
    float z = 1000000.0;
    if(h.x > -1.0){
        vec3 pos = ro + h.x * rd;
        
        if(h.y == 1.0){
        	col *= calcAO(pos, normal(pos));;
            
           
            
            
           
            col *= mirror(pos, rd); 
            col *= shadow(pos, lp) + 0.4;
            
        }
    		
    	
        if(h.y == 2.0){
        	col = vec3(0.0, 0.0, 1.0) * calcAO(pos, normal(pos));
            col *= shadow(pos, lp);
            //float d = h.z; 
            //float s = d / 1.0;
            //s = s / (1.0 + s); 
            
           // col = (1.0 - s) * col + s * vec3(0.7);
        }
        
        
        if(h.y == 3.0) {
        	
            col = vec3(0.7, 0.7, 0.7) * calcAO(pos, normal(pos));
            
            col += checkers(pos);
            col *= mix(col, vec3(0.9), 20.0);
            col *= shadow(pos, lp);
        	
        }
        if(h.y == 4.0) {
        	
            col = vec3(1.0,0.0,0.0) * calcAO(pos, normal(pos)); 
        	col *= shadow(pos, lp);
            
            
        	
        }
        if(h.y == 5.0){
        	if(rand(vec2(rd.x, rd.y)) > 0.0 )
				col = mix(col, vec3(0.0, 0.0, 0.0), 1.2);  
        	
        
        }
        if(h.y == 6.0) {
            col = vec3(1.0,0.0,0.7) * calcAO(pos, normal(pos)); 
        	col *= shadow(pos, lp);
            col += phong_light(pos, -lp, ro, 200.0);
        
        }
        
        if(h.y == 7.0) {
                col = vec3(0.0,1.0,0.7) * calcAO(pos, normal(pos));
                col *= shadow(pos, lp);
                col += phong_light(pos, -lp, ro, 2000.0);
                
        }
        z = pos.z;
        col *= fog(pos);
        
        
    } else {
        col = vec3(0.7, 1.0, 1.5)*exp(-rd.y);
    }
    
    return vec4(col,h.x);


}



float pow2(float x) { return x * x; }

vec3 AntiA(in vec2 uv){
    vec3 col = vec3(0.0);
    
    
    float an = 10.0 * iMouse.x/iResolution.x;
    
    vec3 ro = vec3(4.0*cos(an)*1.5, 1.0, 4.0*sin(an) * 1.5);
    
    
    
    
   
    
    vec3 ta = vec3(0.0); // target for camera


    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize( cross(ww, vec3(0,1,0)));
    vec3 vv = normalize( cross(uu, ww));

    
    vec3 rd = normalize(uv.x*uu + uv.y*vv + ww);
    
    vec4 r = render(ro, rd); 
    
    col += r.xyz;
    
    vec2 cuv = vec2(uv.x + 0.001, uv.y + 0.001);
    rd = normalize(cuv.x*uu + cuv.y*vv + ww);
    
    r = render(ro, rd);
    
    col = mix(col, r.xyz, 0.75);
    
    
    
    cuv = vec2(uv.x + 0.001, uv.y - 0.001);

    rd = normalize(cuv.x*uu + cuv.y*vv + ww);
    
    r = render(ro, rd); 
    
    col = mix(col, r.xyz, 0.75);
    
    
    cuv = vec2(uv.x - 0.001, uv.y - 0.001);
    
    rd = normalize(cuv.x*uu + cuv.y*vv + ww);
    
    r = render(ro, rd); 
    
    col += r.xyz;
    
    
    cuv = vec2(uv.x - 0.001, uv.y + 0.001);
    
    rd = normalize(cuv.x*uu + cuv.y*vv + ww);
    
    r = render(ro, rd); 
    
    col = mix(col, r.xyz, 0.75);
    return col/4.0;
}
void main()
{
    vec2 uv = (2.0 * gl_FragCoord - iResolution.xy)/iResolution.y;
    vec3 col = vec3(0.0);
   
    
    
    float an = 10.0 * iMouse.x/iResolution.x;
    
    vec3 ro = vec3(4.0*cos(an)*1.5, 1.0, 4.0*sin(an) * 1.5);
    
    
    
    vec3 ta = vec3(0.0); // target for camera


    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize( cross(ww, vec3(0,1,0)));
    vec3 vv = normalize( cross(uu, ww));

    
    vec3 rd = normalize(uv.x*uu + uv.y*vv + ww);
    vec4 r = render(ro, rd); 
    col += r.xyz;  

        
    vec3 cur_pos = ro + r.w * rd;
    if(flag > 0.0){ 
        vec4 vFog = volFog(ro, rd);
        col = mix(vFog.xyz,col, vFog.w);
    }
    gl_FragColor = vec4(col, 1.0);
}
""")

program = glCreateProgram()
glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)
glUseProgram(program)

# Определяем массив цветов (по одному цвету для каждой вершины)

glutTimerFunc(10, calc, 0)
iResolution = glGetUniformLocation(program, "iResolution")
glUniform2f(iResolution, 512.0, 512.0)
glutMainLoop()









