from tornado import gen
import csv

class DummyController:

    fixationReceived = False
    fixationBuffer = []
    detectedFixations = []

    countFixations = 0
    receiveFixations = True
    x_from_tobii = []
    y_from_tobii = []
    time_from_tobii = []


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
        writer.writerow(['sample_id', 'isFixation', 'start_time', 'duration', 'end_x', 'end_Y'])
        sample_id = 1
        print("Found fixations %d" % len(DummyController.detectedFixations))
        for values in DummyController.detectedFixations:
            writer.writerow([sample_id] + list(values))
            sample_id = sample_id + 1
        fl.close()


    @gen.coroutine
    def wait_for_fixation_2(self):
        while True:
            if not DummyController.receiveFixations:
                break
            yield
        fl = open('myOnlineFixations.csv', 'wb')
        writer = csv.writer(fl)
        writer.writerow(['sample_id', 'timestamp', 'fix_id', 'duration', 'fix_x', 'fix_Y', 'pt_x', 'pt_y'])
        # First fixation
        curr_fixation = DummyController.fixationBuffer[0]
        fix_id = 1
        isFixation = False
        print("size of x is %d" % len(DummyController.x_from_tobii))
        print("size of fix is %d" % len(DummyController.fixationBuffer))
        for i in range(len(DummyController.x_from_tobii)):
            start, end, xfixation, y_fixation = curr_fixation
            # Out of the current fixation
            if (i > end):
                if (fix_id < len(DummyController.fixationBuffer) - 1):
                    fix_id += 1
                    curr_fixation = DummyController.fixationBuffer[fix_id]
                    start, end, xfixation, y_fixation = curr_fixation
                else:
                    break
            if (i >= start and i <= end):
                isFixation = True
            else:
                isFixation = False
            x = DummyController.x_from_tobii[i]
            y = DummyController.y_from_tobii[i]
            time = DummyController.time_from_tobii[i]
            if (isFixation):
                writer.writerow([i + 1, time, fix_id,  DummyController.time_from_tobii[end] -  DummyController.time_from_tobii[start],  xfixation, y_fixation, x, y])
            else:
                writer.writerow([i + 1, time, -1, -1, 0, 0, x, y])
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
