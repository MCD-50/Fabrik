from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import yaml
from datetime import datetime
import random, string
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from jsonToPrototxt import jsonToPrototxt
import tensorflow as tf
import sys
sys.path.insert(0, BASE_DIR+'/media/tensorflow/')
sys.path.insert(0, BASE_DIR+'/caffe-tensorflow-master/')


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def index(request):
    return render(request, 'cloudcvIde/index.html')


@csrf_exempt
def exportToCaffe(request):
    if request.method == 'POST':
        net = yaml.safe_load(request.POST.get('net'))
        net_name = request.POST.get('net_name')
        if net_name == '':
            net_name = 'Net'
        prototxt,input_dim = jsonToPrototxt(net,net_name)
        randomId=datetime.now().strftime('%Y%m%d%H%M%S')+randomword(5)
        with open(BASE_DIR+'/media/prototxt/'+randomId+'.prototxt', 'w') as f:
            f.write(prototxt)
        return JsonResponse({'result': 'success','id': randomId, 'name': randomId+'.prototxt', 'url': '/media/prototxt/'+randomId+'.prototxt'})


@csrf_exempt
def exportToTensorflow(request):
    if request.method == 'POST':
        net = yaml.safe_load(request.POST.get('net'))
        net_name = request.POST.get('net_name')
        if net_name == '':
            net_name = 'Net'
        prototxt,input_dim = jsonToPrototxt(net,net_name)
        randomId=datetime.now().strftime('%Y%m%d%H%M%S')+randomword(5)
        with open(BASE_DIR+'/media/prototxt/'+randomId+'.prototxt', 'w') as f:
            f.write(prototxt)
        os.system('python '+BASE_DIR+'/caffe-tensorflow-master/convert.py '+BASE_DIR+'/media/prototxt/'+randomId+'.prototxt --code-output-path='+BASE_DIR+'/media/tensorflow/'+randomId+'.py')

        # NCHW to NHWC data format
        input_caffe = map(int,input_dim.split(','))
        input_tensorflow = []
        for i in [0,2,3,1]:
            input_tensorflow.append(input_caffe[i])

        # converting generated caffe-tensorflow code to graphdef
        try:
            net = __import__ (str(randomId))
            images = tf.placeholder(tf.float32, input_tensorflow)
            net = getattr(net, net_name)({'blob0': images})
            graph_def = tf.get_default_graph().as_graph_def(add_shapes=True)
            with open(BASE_DIR+'/media/graphdef/'+randomId+'.pbtxt', 'w') as f: f.write(str(graph_def))
        except AssertionError:
            return JsonResponse({'result': 'error', 'error': 'Cannot convert to GraphDef'})

        return JsonResponse({'result': 'success','id': randomId, 'name': randomId+'.pbtxt', 'url': '/media/graphdef/'+randomId+'.pbtxt'})

