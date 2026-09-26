%cd /content/guardian\_angel  
import tensorflow as tf  
import os

model \= tf.keras.models.load\_model("models/seizure\_detection\_model.h5")

converter \= tf.lite.TFLiteConverter.from\_keras\_model(model)  
converter.target\_spec.supported\_ops \= \[  
    tf.lite.OpsSet.TFLITE\_BUILTINS,  
    tf.lite.OpsSet.SELECT\_TF\_OPS  \# needed for some LSTM operations  
\]

tflite\_model \= converter.convert()

with open("models/seizure\_detection\_model.tflite", "wb") as f:  
    f.write(tflite\_model)

h5\_size \= os.path.getsize("models/seizure\_detection\_model.h5") / 1024  
tflite\_size \= os.path.getsize("models/seizure\_detection\_model.tflite") / 1024  
print(f"Original .h5 size: {h5\_size:.1f} KB")  
print(f"TFLite size: {tflite\_size:.1f} KB")  
print(f"Size reduction: {(1 \- tflite\_size/h5\_size)\*100:.1f}%")

OUTPUT:  
WARNING:absl:Compiled the loaded model, but the compiled metrics have yet to be built. \`model.compile\_metrics\` will be empty until you train or evaluate the model.

/content/guardian\_angel  
Saved artifact at '/tmp/tmpbgezdygz'. The following endpoints are available:

\* Endpoint 'serve'  
  args\_0 (POSITIONAL\_ONLY): TensorSpec(shape=(None, 250, 6), dtype=tf.float32, name='signal\_input')  
Output Type:  
  TensorSpec(shape=(None, 1), dtype=tf.float32, name=None)  
Captures:  
  138023814038736: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814040464: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814041424: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814053520: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814047760: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814052752: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814047568: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023814053712: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368585488: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368585296: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368583376: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368583568: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368584912: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368585680: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368583184: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368582992: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368581072: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368585104: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368581456: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368581264: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368580880: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368580688: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368578768: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368582800: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368579152: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368578960: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368578576: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368577232: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368576464: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368579344: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368576848: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368574928: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368576656: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368574544: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368587216: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368575120: TensorSpec(shape=(), dtype=tf.resource, name=None)  
  138023368587600: TensorSpec(shape=(), dtype=tf.resource, name=None)  
Original .h5 size: 915.3 KB  
TFLite size: 286.6 KB  
Size reduction: 68.7%

