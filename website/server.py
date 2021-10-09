from flask import Flask, render_template, jsonify, request
from random import randrange

from pyecharts import options as opts
from pyecharts.charts import Line

import json

import time

from pyecharts.charts.base import default


class PowerSupply:
  def __init__(self, data_num=300):
    self.data_num = data_num
    self.times = [self.__get_time__()]
    self.datas = {"flags": [None],
                  "u_in": [None],
                  "i_in": [None],
                  "p_in": [None],
                  "u_out": [None],
                  "i_out": [None],
                  "p_out": [None],
                  "t_intake": [None],
                  "t_internal": [None],
                  "fan_speed": [None],
                  "on_seconds": [None],
                  "max_p_in": [None],
                  "max_i_in": [None],
                  "max_i_out": [None],
                  "fan_target": [None]}

    self.__convert_dict = {"REG2":  ["flags", 1],
                           "REG8":  ["u_in", 32.],
                           "REGa":  ["i_in", 128.],
                           "REGc":  ["p_in", 2.],
                           "REGe":  ["u_out", 254.5],
                           "REG10": ["i_out", 128.],
                           "REG12": ["p_out", 2.],
                           "REG1a": ["t_intake", 32.],
                           "REG1c": ["t_internal", 32.],
                           "REG1e": ["fan_speed", 1.],
                           "REG30": ["on_seconds", 2.],
                           "REG32": ["max_p_in", 2.],
                           "REG34": ["max_i_in", 128.],
                           "REG36": ["max_i_out", 128.],
                           "REG40": ["fan_target", 1.]}


  def __get_time__(self):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

  def convert_register_read(self, reg, read_in):
    reg_name = self.__convert_dict[reg][0]
    if read_in == 65535:
      return reg_name, None
    else:
      value = read_in / self.__convert_dict[reg][1]
      if reg_name in ["t_intake", "t_internal"]:
        value = (value - 32) / 1.8
      return reg_name, value
    

  def register_data(self, data_in):
    if len(self.times) >= self.data_num:
      self.times = self.times[1-self.data_num:]
      for data_key in self.datas:
        self.datas[data_key] = self.datas[data_key][1-self.data_num:]

    self.times.append(self.__get_time__())

    for data_key in self.datas:
      data = self.datas[data_key]

      data.append(data_in.get(data_key, None))

  def pack_data(self, data_key):
    return list(zip(self.times, self.datas[data_key]))

  def last_data(self, data_key):
    return self.datas[data_key][-1]

ps = PowerSupply()

app = Flask(__name__)
app.debug=True

def register_test_data(power_supply):
  u_in = randrange(210, 230)
  i_in = randrange(1, 10)
  p_in = u_in * i_in

  u_out = randrange(110, 130) / 10.
  i_out = randrange(100, 200) / 10.
  p_out = u_out * i_out

  ps.register_data({"u_in": u_in,
                    "i_in": i_in,
                    "p_in": p_in,
                    "u_out": u_out,
                    "i_out": i_out,
                    "p_out": p_out})

def input_chart_base() -> Line:
  line = (
    Line()
    .add_xaxis(ps.times)
    .add_yaxis(
      "U", ps.datas["u_in"],
      is_symbol_show=False,
      is_smooth=True,
      label_opts=opts.LabelOpts(is_show=False),
    )
    .set_global_opts(
      title_opts=opts.TitleOpts(title="Input Monitor"),
      xaxis_opts=opts.AxisOpts(type_="time"),
      yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} V")),
      tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
    .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} A")))
    .add_yaxis(
      "I", ps.datas["i_in"],
      is_symbol_show=False,
      is_smooth=True,
      label_opts=opts.LabelOpts(is_show=False),
      yaxis_index=1
    )
  )

  return line

def output_chart_base() -> Line:
  line = (
    Line()
    .add_xaxis(ps.times)
    .add_yaxis(
      "U", ps.datas["u_out"],
      is_symbol_show=False,
      is_smooth=True,
      label_opts=opts.LabelOpts(is_show=False),
    )
    .set_global_opts(
      title_opts=opts.TitleOpts(title="Output Monitor"),
      xaxis_opts=opts.AxisOpts(type_="time"),
      yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} V")),
      tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
    .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} A")))
    .add_yaxis(
      "I", ps.datas["i_out"],
      is_symbol_show=False,
      is_smooth=True,
      label_opts=opts.LabelOpts(is_show=False),
      yaxis_index=1
    )
  )

  return line

def misc_chart_base() -> Line:
  line = (
    Line()
    .add_xaxis(ps.times)
    .set_global_opts(
      title_opts=opts.TitleOpts(title="Misc Monitor"),
      xaxis_opts=opts.AxisOpts(type_="time"),
      tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
  )
  for data_key in ["p_in", "p_out", "t_intake", "t_internal", "fan_speed"]:
    line.add_yaxis(data_key, ps.datas[data_key],
      is_symbol_show=False,
      is_smooth=True,
      label_opts=opts.LabelOpts(is_show=False),
    )

  return line

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/PowerSupplyMonitor/inputMonitor")
def input_page():
  return render_template("inputMonitor.html")


@app.route("/PowerSupplyMonitor/api/inputChart")
def get_input_chart():
  c = input_chart_base()
  return c.dump_options_with_quotes()


@app.route("/PowerSupplyMonitor/api/inputDynamicData")
def update_input_data():
  # register_test_data(ps)

  return jsonify({"value0": ps.pack_data("u_in"), "value1": ps.pack_data("i_in")})


@app.route("/PowerSupplyMonitor/outputMonitor")
def output_page():
  return render_template("outputMonitor.html")


@app.route("/PowerSupplyMonitor/api/outputChart")
def get_output_chart():
  c = output_chart_base()
  return c.dump_options_with_quotes()


@app.route("/PowerSupplyMonitor/api/outputDynamicData")
def update_output_data():
  # register_test_data(ps)

  return jsonify({"value0": ps.pack_data("u_out"), "value1": ps.pack_data("i_out")})


@app.route("/PowerSupplyMonitor/miscMonitor")
def misc_page():
  return render_template("miscMonitor.html")


@app.route("/PowerSupplyMonitor/api/miscChart")
def get_misc_chart():
  c = misc_chart_base()
  return c.dump_options_with_quotes()


@app.route("/PowerSupplyMonitor/api/miscDynamicData")
def update_misc_data():
  # register_test_data(ps)

  return jsonify({"p_in": ps.pack_data("p_in"), "p_out": ps.pack_data("p_out"),
                  "t_intake": ps.pack_data("t_intake"), "t_internal": ps.pack_data("t_internal"),
                  "fan_speed": ps.pack_data("fan_speed"), "flags": ps.last_data("flags"), 
                  "on_seconds": ps.last_data("on_seconds"), "max_p_in": ps.last_data("max_p_in"),
                  "max_i_in": ps.last_data("max_i_in"), "max_i_out": ps.last_data("max_i_out"),
                  "fan_target": ps.last_data("fan_target")
                  })


@app.route("/receiveData", methods=["POST"])
def get_data():
  print("Receive")
  raw_datas = json.loads(request.get_data(as_text=True))
  datas = {}
  for data_key in raw_datas:
    data_key, value = ps.convert_register_read(data_key, raw_datas[data_key])
    datas[data_key] = value

  ps.register_data(datas)

  return jsonify({})
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)