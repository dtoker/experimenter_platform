from tornado import gen
import csv

class DummyController:

    fixationReceived = False
    fixationBuffer = []
    detectedFixations = []
    countFixations = 0
    receiveFixations = True

    @gen.coroutine
    def wait_for_fixation(self):
        AOI_defitions = [[(300, 300), (500, 300), (300 , 500), (500, 500)]]
        while True:
            if not DummyController.fixationReceived:
                if not DummyController.receiveFixations:
                    break
                yield
            else:
                for fix in DummyController.fixationBuffer:
                    DummyController.detectedFixations.append(fix)
                    print("Found fixation with coords %d, %d in AOI" % (fix[3], fix[4]))
                    DummyController.countFixations += 1
                DummyController.fixationBuffer = []
                DummyController.fixationReceived = False
                if not DummyController.receiveFixations:
                    break
        fl = open('myOnlineFixations.csv', 'wb')
        writer = csv.writer(fl)
        writer.writerow(['fixation_index', 'start_time', 'end_time', 'duration', 'end_x', 'end_Y'])
        fixation_index = 1
        print("Found fixations %d" % len(DummyController.detectedFixations))
        for values in DummyController.detectedFixations:
            writer.writerow([fixation_index] + list(values))
            fixation_index = fixation_index + 1
        fl.close()

def fixation_inside_aoi(x,y,poly):
    """Determines if a point is inside a given polygon or not

        The algorithm is called "Ray Casting Method".

    Args:
        poly: is a list of (x,y) pairs defining the polgon

    Returns:
        True or False.
    """
    n = len(poly)

    if n==0:
        return False

    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
