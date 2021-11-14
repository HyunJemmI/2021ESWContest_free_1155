import tflite_runtime.interpreter as tflite
import csv
import io
import numpy as np
import matplotlib.pyplot as plt

def getcsv(path):
#     try:
    csvDetails = io.StringIO(open(path).read())
    classNames = [className for (classIndex, mid, className) in csv.reader(csvDetails)]
    classNames = classNames[1:]
    return classNames
#     except Exception as e:
#         print('csv파일을 불러오지 못했습니다!')
#         print(e)
#         return [(i,i,i)for i in range(521)]

class Classificate:
    '''
    Classificate - 소리 분류
    -----함수-----
    tonumpy(data)
    preprocess(data)
    classifier(data)
    pltshow(data)
    ----------------
    시작 시 모델, csv파일 읽음
    '''
    def __init__(self):
        stat=1
        try:
            print('모델 로딩')
            self.model = tflite.Interpreter(model_path = 'yamnet.tflite')
        except Exception as e:
            print('모델을 불러올 수 없습니다!')
            print(e)
            stat = 0
        else:
            print('성공')
            self.classNames = getcsv('yamnet_class_map.csv')

            input_details = self.model.get_input_details()
            self.waveform_input_index = input_details[0]['index']
            output_details = self.model.get_output_details()
            self.scores_output_index = output_details[0]['index']
            self.embeddings_output_index = output_details[1]['index']
            self.spectrogram_output_index = output_details[2]['index']

            
    def tonumpy(self, buff):
        '''
        tonumpy(data)
        넘파이 배열로 변환
        반환값: 처리된 data
        '''
        data = np.array([])
        for i in buff:
            arr = np.frombuffer(i, dtype = np.int32).astype(np.float32)
            data = np.concatenate((data,arr),axis = None)
        return data.astype(np.float32)
            
        
    def preprocess(self, data):
        '''
        preprocess(data) *numpy data*
        [-1,1] 크기 전처리 함수
        반환값: 처리된 data
        '''
        max = np.max(np.abs(data))
        if(max > 1):
            for i in range(len(data)):
                data[i] = data[i]/max
            return data
        else:
            return data

    def pltShow(self, data):
        '''
        pltshow(data)
        데이터 타입, 파형 확인
        디버깅용
        '''
        print('데이터 타입= ', data.dtype)
        plt.plot(data)
        plt.show()
    def classifier(self, data):
        '''
        classifier(data)
        소리 분류 함수
        반환값: 예상값 2개
        '''
        data = np.delete(data,1)
        print(len(data))
        self.model.resize_tensor_input(self.waveform_input_index, [len(data)])
        self.model.allocate_tensors()
        self.model.set_tensor(self.waveform_input_index, data)
        self.model.invoke()
        scores, embeddings, spectrogram = (
                                            self.model.get_tensor(self.scores_output_index),
                                            self.model.get_tensor(self.embeddings_output_index),
                                            self.model.get_tensor(self.spectrogram_output_index))
        mean = scores.mean(axis = 0)
        return self.classNames[mean.argsort()[-1]]

    
'''
모듈확인용 직접실행
'''
if __name__=="__main__":
    clf = Classificate
    data = np.zeros(100000)
    clf.tonumpy(data)
    clf.equalizer(data)
    clf.pltShow(data)
    print(clf.classifier(data))




