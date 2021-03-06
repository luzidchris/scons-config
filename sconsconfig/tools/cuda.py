"""
SCons.Tool.cuda

CUDA Tool for SCons

"""

import os, sys
import SCons.Tool
import SCons.Scanner.C
import SCons.Defaults

CUDAScanner = SCons.Scanner.C.CScanner()

# this object emitters add '.linkinfo' suffixed files as extra targets
# these files are generated by nvcc. The reason to do this is to remove
# the extra .linkinfo files when calling scons -c
def CUDANVCCStaticObjectEmitter(target, source, env):
	tgt, src = SCons.Defaults.StaticObjectEmitter(target, source, env)
	for file in src:
		lifile = os.path.splitext(src[0].rstr())[0] + '.linkinfo'
		tgt.append(lifile)
	return tgt, src
def CUDANVCCSharedObjectEmitter(target, source, env):
	tgt, src = SCons.Defaults.SharedObjectEmitter(target, source, env)
	for file in src:
		lifile = os.path.splitext(src[0].rstr())[0] + '.linkinfo'
		tgt.append(lifile)
	return tgt, src

bad_flags_set = set(['-malign-double'])
def strip_flags(target, source, env, for_signature):
	flags = env['CCFLAGS']
	if isinstance(flags, basestring):
		flags = [flags]
	return [f for f in flags if f not in bad_flags_set]
		

def generate(env):
	staticObjBuilder, sharedObjBuilder = SCons.Tool.createObjBuilders(env);
	staticObjBuilder.add_action('.cu', '$STATICNVCCCMD')
#	staticObjBuilder.add_emitter('.cu', CUDANVCCStaticObjectEmitter)
	sharedObjBuilder.add_action('.cu', '$SHAREDNVCCCMD')
#	sharedObjBuilder.add_emitter('.cu', CUDANVCCSharedObjectEmitter)
	SCons.Tool.SourceFileScanner.add_scanner('.cu', CUDAScanner)
	
	# default compiler
	env['NVCC'] = 'nvcc'
	env['NVCCFLAGS'] = ''
	
	# default flags for the NVCC compiler
	env['ENABLESHAREDNVCCFLAG'] = '-shared'

	# default NVCC commands
	env['cuda_strip_flags'] = strip_flags
	env['STATICNVCCCMD'] = '$NVCC -o $TARGET -c $NVCCFLAGS $cuda_strip_flags $_CCCOMCOM $SOURCES'
	env['SHAREDNVCCCMD'] = '$NVCC -o $TARGET -c $NVCCFLAGS $cuda_strip_flags $_CCCOMCOM $ENABLESHAREDNVCCFLAG $SOURCES'

	# helpers
	home=os.environ.get('HOME', '')
	programfiles=os.environ.get('PROGRAMFILES', '')
	homedrive=os.environ.get('HOMEDRIVE', '')
	
	# find CUDA Toolkit path and set CUDA_TOOLKIT_PATH
	cudaToolkitPath = None
	try:
		cudaToolkitPath = env['CUDA_TOOLKIT_PATH']
	except:
		paths=[home + '/NVIDIA_CUDA_TOOLKIT',
		       home + '/Apps/NVIDIA_CUDA_TOOLKIT',
			   home + '/Apps/NVIDIA_CUDA_TOOLKIT',
			   home + '/Apps/CudaToolkit',
			   home + '/Apps/CudaTK',
			   '/usr/local/NVIDIA_CUDA_TOOLKIT',
			   '/usr/local/CUDA_TOOLKIT',
			   '/usr/local/cuda_toolkit',
			   '/usr/local/CUDA',
			   '/usr/local/cuda',
			   '/Developer/NVIDIA CUDA TOOLKIT',
			   '/Developer/CUDA TOOLKIT',
			   '/Developer/CUDA',
			   programfiles + 'NVIDIA Corporation/NVIDIA CUDA TOOLKIT',
			   programfiles + 'NVIDIA Corporation/NVIDIA CUDA',
			   programfiles + 'NVIDIA Corporation/CUDA TOOLKIT',
			   programfiles + 'NVIDIA Corporation/CUDA',
			   programfiles + 'NVIDIA/NVIDIA CUDA TOOLKIT',
			   programfiles + 'NVIDIA/NVIDIA CUDA',
			   programfiles + 'NVIDIA/CUDA TOOLKIT',
			   programfiles + 'NVIDIA/CUDA',
			   programfiles + 'CUDA TOOLKIT',
			   programfiles + 'CUDA',
			   homedrive + '/CUDA TOOLKIT',
			   homedrive + '/CUDA']
		for path in paths:
			if os.path.isdir(path):
				print 'scons: CUDA Toolkit found in ' + path
				cudaToolkitPath = path
				break
		if cudaToolkitPath == None:
			sys.exit("Cannot find the CUDA Toolkit path. Please modify your SConscript or add the path in cudaenv.py")
	env['CUDA_TOOLKIT_PATH'] = cudaToolkitPath

	# find CUDA SDK path and set CUDA_SDK_PATH
	cudaSDKPath = None
	try:
		cudaSDKPath = env['CUDA_SDK_PATH']
	except:
		paths=[home + '/NVIDIA_CUDA_SDK', # i am just guessing here
		       home + '/Apps/NVIDIA_CUDA_SDK',
			   home + '/Apps/CudaSDK',
			   '/usr/local/NVIDIA_CUDA_SDK',
			   '/usr/local/CUDASDK',
			   '/usr/local/cuda_sdk',
			   '/Developer/NVIDIA CUDA SDK',
			   '/Developer/CUDA SDK',
			   '/Developer/CUDA',
			   programfiles + 'NVIDIA Corporation/NVIDIA CUDA SDK',
			   programfiles + 'NVIDIA/NVIDIA CUDA SDK',
			   programfiles + 'NVIDIA CUDA SDK',
			   programfiles + 'CudaSDK',
			   homedrive + '/NVIDIA CUDA SDK',
			   homedrive + '/CUDA SDK',
			   homedrive + '/CUDA/SDK']
		for path in paths:
			if os.path.isdir(path):
				print 'scons: CUDA SDK found in ' + path
				cudaSDKPath = path
				break
		if cudaSDKPath == None:
			sys.exit("Cannot find the CUDA SDK path. Please set env['CUDA_SDK_PATH'] to point to your SDK path")
	env['CUDA_SDK_PATH'] = cudaSDKPath
	
	# cuda libraries
	if env['PLATFORM'] == 'posix':
		cudaSDKSubLibDir = '/linux'
	elif env['PLATFORM'] == 'darwin':
		cudaSDKSubLibDir = '/darwin'
	else:
		cudaSDKSubLibDir = ''

	# add nvcc to PATH
	env.PrependENVPath('PATH', cudaToolkitPath + '/bin')
	
	# add required libraries
	env.Append(CPPPATH=[cudaSDKPath + '/common/inc', cudaToolkitPath + '/include'])
	env.Append(LIBPATH=[cudaSDKPath + '/lib', cudaSDKPath + '/common/lib' + cudaSDKSubLibDir, cudaToolkitPath + '/lib'])
	env.Append(LIBS=['cudart'])

def exists(env):
	return env.Detect('nvcc')
