import math
import copy

class PathSegment(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def scale(self, cx, cy=None):
        if cy is None:
            cy = cx
        self.x = cx*self.x
        self.y = cy*self.y
        return self
        
    def translate(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
        return self
        
    def rotate(self, deg, cx=0, cy=0):
        r = math.radians(deg)
        self.x, self.y = self.x*math.cos(r) - self.y*math.sin(r), self.x*math.sin(r) + self.y*math.cos(r)
        return self

class MoveTo(PathSegment):
    def __str__(self):
        return 'M {0} {1}'.format(self.x, self.y)

class LineTo(PathSegment):   
    def __str__(self):
        return 'L {0} {1}'.format(self.x, self.y)
        
class ClosePath(PathSegment):
    def __init__(self):
        self.x = 0
        self.y = 0
        
    def __str__(self):
        return 'Z'
    
class ArcTo(PathSegment):
    def __init__(self, x, y, rx, ry, x_rot=0, large_arc=0, sweep=0):
        self.rx = rx
        self.ry = ry
        self.x_rot = x_rot
        self.large_arc = large_arc
        self.sweep = sweep
        self.x = x
        self.y = y
   
    def scale(self, cx, cy=None):
        if cy is None:
            cy = cx
        self.x = cx*self.x
        self.y = cy*self.y
        self.rx = cx*self.rx
        self.ry = cy*self.ry
        return self
        
    def __str__(self):
        return 'A {0} {1} {2} {3} {4} {5} {6}'.format(
            self.rx, 
            self.ry,
            self.x_rot,
            self.large_arc,
            self.sweep,
            self.x,
            self.y
        )

class Path(object):
    def __init__(self, stroke, stroke_width, fill="transparent"):
        self.data = []
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill = fill
        
    def add(self, segment):
        if isinstance(segment, Path):
            for sub_segment in segment.copy().data:
                self.add(sub_segment)
        else:
            self.data.append(segment)
        
    def close(self):
        self.data.append(ClosePath())
        
    def scale(self, cx, cy=None):
        self.data = [x.scale(cx, cy) for x in self.data]
        return self
        
    def translate(self, dx, dy):
        self.data = [x.translate(dx, dy) for x in self.data]
        return self
        
    def rotate(self, deg, cx=0, cy=0):
        self.data = [x.rotate(deg, cx, cy) for x in self.data]
        return self
        
    def reverse(self):
        x, y = self.get_last_coordinates()
        data = []
        data.append(MoveTo(x, y))
        if isinstance(self.data[-1], ClosePath):
            self.data[-1] = LineTo(x,y)
        for i,seg in enumerate(self.data[-1:0:-1]):
            next_seg = self.data[-(i+2)]
            seg.x = next_seg.x
            seg.y = next_seg.y
            if isinstance(seg, ArcTo):
                seg.sweep = int(not seg.sweep)
            data.append(seg)
        self.data = data
        return self
        
    def get_last_coordinates(self):
        if isinstance(self.data[-1], ClosePath):
            seg = self.data[0]
        else:
            seg = self.data[-1]
        return seg.x, seg.y
        
    def copy(self):
        return copy.deepcopy(self)
        
    def __str__(self):
        return """
            <path d="{0}" stroke="{1}" stroke-width="{2}" fill="{3}"/>
            """.format(
                ' '.join([str(x) for x in self.data]),
                self.stroke,
                self.stroke_width,
                self.fill).strip()
                
class SVG(object):
    def __init__(self):
        self.elements = []
        
    def add(self, element):
        self.elements.append(element)
        
    def __str__(self):
        return """
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              {0}
            </svg>""".format('\n'.join([str(x) for x in self.elements])).strip()
        
        
if __name__ == '__main__':
    tongue = Path('black', 2)
    tongue.add(LineTo(1.1, 0))
    tongue.add(LineTo(1.1, -0.1))
    tongue.add(ArcTo(1.45, -0.1, 0.3, 0.3, large_arc=1, sweep=1))
    tongue.add(LineTo(1.45, 0))
    tongue.add(LineTo(2, 0))
    t2 = tongue.copy()
    tongue.rotate(60).translate(9,0)
    t2.scale(-1).rotate(-60).translate(1,0).reverse()
    t2.data = t2.data[1:]
    
    p = Path('black', 2)
    rt3 = 3**0.5
    p.add(MoveTo(1, 0))
    p.add(LineTo(3, 0))
    p.add(LineTo(4, rt3))
    p.add(LineTo(6, rt3))
    p.add(LineTo(7, 0))
    p.add(LineTo(9, 0))
    p.add(tongue)
    p.add(ArcTo(0, rt3, 10, 10, sweep=1))
    p.add(t2)
    p.close()
    p.scale(25).translate(200, 500)
    s = SVG()
    s.add(p)
    
    for _ in range(5):
        p = s.elements[-1].copy()
        home = p.data[0].x, p.data[0].y
        next = p.data[5].x, p.data[5].y
        p.translate(-home[0], -home[1]).rotate(-60).translate(next[0], next[1])
        s.add(p)
    
    """
    for d in range(0,61,10):
        s.add(copy.deepcopy(p).rotate(d))
    """
    print str(s)
    with open('test4.svg', 'wb') as f:
        f.write(str(s))