import random

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
tableau20 = ['rgb({:f},{:f},{:f})'.format(r/255.0,g/255.0,b/255.0)  for (r,g,b) in tableau20]


def get_next_color(previous_colors):
    num_used_colors = len(previous_colors)
    if num_used_colors < 20:
        return tableau20[num_used_colors+1]
    else:
        r = random.randint(0, 255)/255.0
        g = random.randint(0, 255)/255.0
        b = random.randint(0, 255)/255.0
        new_color = 'rgb({:f},{:f},{:f})'.format(r,g,b)
        if new_color in previous_colors:
            return get_next_color(previous_colors)
        else:
            return new_color
