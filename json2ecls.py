import json
import sys

class JSON2ECL(object):
    def __init__(self, JSON, name=''):
        self.JSON = JSON
        self.ECL = ""
        self.nextcode = 1
        self.curcode = 0
        self.loop_code_stack = []
        self.next_loop_code = 0
        self.ecl_blocks = [""]
        if not name:
            self.name = 'JTE'
        else:
            self.name = name
    
    def get_json(self):
        return self.json_data
    
    def parse(self):
        if not self.ECL:
            self.translate()
        return self.ECL
    
    def get_next_code(self):
        cur = self.nextcode
        #self.nextcode += 1
        return cur

    def get_next_loop_code(self):
        cur = self.next_loop_code
        self.next_loop_code += 1
        return cur

    def bullet_parser(self, danmaku, name):

        img_code = danmaku.get('img-type', 1)
        color_code = danmaku.get('color', 1)
        dir_angle = danmaku.get('direction', 0)
        speed = danmaku.get('speed', 1)
        style = danmaku.get('style')

        position = danmaku.get('position', {})
        x = position.get('x', 0)
        y = position.get('y', 0)

        waitframe = danmaku.get('wait', 0)

        #loop_info = danmaku.get('loop', {})
        #loop_time = loop_info.get('time')
        #loop_int = loop_info.get('interval')

        way_info = danmaku.get('way', {})
        way_num = way_info.get('num', 1)
        way_offset = way_info.get('offset-angle', 0)

        layer_info = danmaku.get('layer', {})
        layer_num = layer_info.get('num', 1)
        layer_minspeed = layer_info.get('min-speed', -1)

        sound_info = danmaku.get('sound', {})
        sound_shoot = sound_info.get('shoot', 1)
        sound_turn = sound_info.get('turn', -1)

        #if loop_info:
        #    self.loop_start(loop_time, loop_int)
        danmaku_ecl = ""
        danmaku_ecl += self.ecl_begin(name)

        danmaku_ecl += self.bullet_begin()

        danmaku_ecl += self.set_bullet_image(img_code, color_code)
        danmaku_ecl += self.set_bullet_position(x, y)
        danmaku_ecl += self.set_bullet_dir(dir_angle, way_offset)
        danmaku_ecl += self.set_bullet_speed(speed, layer_minspeed)
        danmaku_ecl += self.set_bullet_way_layer(way_num, layer_num)

        if sound_info:
            danmaku_ecl += self.set_bullet_sound(sound_shoot, sound_turn)

        if style:
            danmaku_ecl += self.set_bullet_style(style)

        danmaku_ecl += self.bullet_end()
        danmaku_ecl += self.wait(waitframe)
        danmaku_ecl += self.ecl_return()
        danmaku_ecl += self.ecl_end()
        #if loop_info:
        #    self.loop_end()
        return danmaku_ecl

    def translate(self):
        self.ecl_blocks[0] += self.ecl_begin('main')
        for danmaku in self.JSON['danmaku']:
            Type = danmaku.get('type','bullet')
            if Type=="bullet":
                code = len(self.ecl_blocks)
                self.ecl_blocks[0] += self.ecl_call(code)
                self.ecl_blocks.append(self.bullet_parser(danmaku, code))
        
        self.ecl_blocks[0] += self.ecl_end()
        self.ECL = '\n'.join(self.ecl_blocks)

    def ecl_call(self, name):
        return 'ins_11("{}");\n'.format(self.ecl_name(name))

    def ecl_name(self, name):
        return '{}_{}'.format(self.name, name)

    def ecl_begin(self, name):
        return 'sub {}_{}(){{\n'.format(self.name, str(name)) + 'var ;\n'

    def ecl_end(self):
        return '}\n'
    
    def ecl_return(self):
        return 'ins_10();\n'

    def bullet_begin(self):
        self.curcode = self.get_next_code()
        return 'ins_600(%d);\n'%self.curcode
    
    def bullet_end(self):
        return 'ins_601(%d);\n'%self.curcode
    
    def wait(self, frame):
        return 'ins_23(%d);\n'%frame

    '''def loop_start(self, time, interval):
        code = self.get_next_loop_code()
        self.loop_code_stack.append((code, time, interval))
        
        return 'goto JTE_LOOP_%d_2 @ 0;\n'%(code)
        return 'JTE_LOOP_%d_1:\n'%(code)

    def loop_end(self):
        code, time, interval = self.loop_code_stack.pop()
        if time==-1:
            time = 10000000
        
        return 'ins_23(%d);\n'%(interval)
        return 'JTE_LOOP_%d_2:\n'%(code)
        return 'if (ins_78(%d) != 1) goto JTE_LOOP_%d_1 @ 0;\n'%(time, code)
    '''
    def set_bullet_image(self, img_code, color_code):
        return 'ins_602(%d, %d, %d);\n'%(self.curcode, img_code, color_code)
    
    def set_bullet_position(self, x, y):
        return 'ins_603(%d, %ff, %ff);\n'%(self.curcode, x, y)
    
    def set_bullet_dir(self, dir_angle, way_offset_angle=0):
        return 'ins_604(%d, %ff, %ff);\n'%(self.curcode, dir_angle, way_offset_angle)
    
    def set_bullet_speed(self, speed, min_speed=-1):
        if min_speed==-1:
            min_speed = speed
        return 'ins_605(%d, %ff, %ff);\n'%(self.curcode, speed, min_speed)
    
    def set_bullet_way_layer(self, way_num, layer_num):
        return 'ins_606(%d, %d, %d);\n'%(self.curcode, way_num, layer_num)
    
    def set_bullet_style(self, style_code):
        return 'ins_607(%d, %d);\n'%(self.curcode, style_code)
    
    def set_bullet_sound(self, shoot_sound, turn_sound):
        return 'ins_608(%d, %d, %d);\n'%(self.curcode, shoot_sound, turn_sound)

if __name__=='__main__':
    if len(sys.argv) != 2:
        pass
    else:
        json_file = open(sys.argv[1])
        json_data = json.load(json_file)
        json_file.close()
        J = JSON2ECL(json_data)
        ecl_file = open('ecl.txt', 'w')
        ecl_file.write(J.parse())
        ecl_file.close()
