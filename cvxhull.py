import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import NullLocator
from matplotlib import rcParams
from scipy.spatial import ConvexHull
import numpy as np
from PIL import Image
import math
from bounding_rectangle import minimum_bounding_rectangle 

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

def render_latex(txt):
    #txt = r"The \emph{characteristic polynomial} $\chi(\lambda)$ of the $3 \times 3$~matrix \\ $\left( \begin{array}{ccc} a & b & c \\ d & e & f \\g & h & i \end{array} \right) $ \\is given by the formula\\ $ \chi(\lambda) = \left| \begin{array}{ccc} \lambda - a & -b & -c \\ -d & \lambda - e & -f \\ -g & -h & \lambda - i \end{array} \right|. $"
    plt.text(0.0, 0.0, txt, fontsize=14)
    ax = plt.gca()
    ax.set_axis_off()
    plt.subplots_adjust(0,0,1,1,0,0)
    plt.margins(0, 0)
    ax.xaxis.set_major_locator(NullLocator())
    ax.yaxis.set_major_locator(NullLocator())
    plt.tight_layout()
    plt.savefig('latex.png', pad_inches=0, bbox_inches='tight')

    import matplotlib.pyplot as plt

    im = Image.open('latex.png').convert("L")
    arr = np.asarray(im)
    x, y = np.where(arr != 255)
    points = list(zip(x, y))
    points = np.array([np.array(p) for p in points])

    bbox = minimum_bounding_rectangle(points)

    LR = np.array((np.ceil(np.max(bbox[:,0])), 
                   np.floor(np.min(bbox[:,1]))))
    LL = np.array((np.floor(np.min(bbox[:,0])), 
                   np.floor(np.min(bbox[:,1]))))
    UL = np.array((np.floor(np.min(bbox[:,0])), 
                   np.ceil(np.max(bbox[:,1]))))
    UR = np.array((np.ceil(np.max(bbox[:,0])), 
                   np.ceil(np.max(bbox[:,1]))))
    rect = np.vstack((LR, LL, UL, UR))
    bounded_image = arr[int(LL[0]):int(UR[0]), int(LL[1]):int(UR[1])]
    Image.fromarray(bounded_image).save('latex.png')
