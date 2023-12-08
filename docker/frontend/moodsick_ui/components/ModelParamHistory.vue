<template>
  <div>
    Model Parameter Aggregates by Mood
    <div id="modelParamaHistory" style="height: 80vh; width: 100%"></div>
  </div>
</template>
  
  <script>
import * as echarts from "echarts";

export default {
  props: ["graphData"],
  mounted() {
    this.$nextTick(() => {
      var app = {};
      var chartDom = document.getElementById("modelParamaHistory");
      var myChart = echarts.init(chartDom);
      var option;
      let xAxisKeys = Object.keys(this.graphData),
        legendData = Object.keys(
          this.graphData[Object.keys(this.graphData)[0]]
        );
        xAxisKeys.sort()

      const posList = [
        "left",
        "right",
        "top",
        "bottom",
        "inside",
        "insideTop",
        "insideLeft",
        "insideRight",
        "insideBottom",
        "insideTopLeft",
        "insideTopRight",
        "insideBottomLeft",
        "insideBottomRight",
      ];
      app.configParameters = {
        rotate: {
          min: -90,
          max: 90,
        },
        align: {
          options: {
            left: "left",
            center: "center",
            right: "right",
          },
        },
        verticalAlign: {
          options: {
            top: "top",
            middle: "middle",
            bottom: "bottom",
          },
        },
        position: {
          options: posList.reduce(function (map, pos) {
            map[pos] = pos;
            return map;
          }, {}),
        },
        distance: {
          min: 0,
          max: 100,
        },
      };
      app.config = {
        rotate: 90,
        align: "left",
        verticalAlign: "middle",
        position: "insideBottom",
        distance: 15,
        onChange: function () {
          const labelOption = {
            rotate: app.config.rotate,
            align: app.config.align,
            verticalAlign: app.config.verticalAlign,
            position: app.config.position,
            distance: app.config.distance,
          };
          myChart.setOption({
            series: [
              {
                label: labelOption,
              },
              {
                label: labelOption,
              },
              {
                label: labelOption,
              },
              {
                label: labelOption,
              },
            ],
          });
        },
      };
      const labelOption = {
        // show: true,
        position: app.config.position,
        distance: app.config.distance,
        align: app.config.align,
        verticalAlign: app.config.verticalAlign,
        rotate: app.config.rotate,
        formatter: "{c}  {name|{a}}",
        fontSize: 16,
        rich: {
          name: {},
        },
      };
      let seriesData = [];
      for (const key of legendData) {
        console.log(key);
        let temp_arr = [];
        for (let index = 0; index < xAxisKeys.length; index++) {
          const element = xAxisKeys[index];
          //  console.log( this.graphData[element][key])
          temp_arr.push(this.graphData[element][key])

        }
        seriesData.push({
          name: key,
          type: "bar",
          barGap: 0,
          label: labelOption,
          emphasis: {
            focus: "series",
          },
          data: temp_arr,
        });
      }
      option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          data: legendData,
          show: false
        },
        grid: {
          containLabel: true
        },
        toolbox: {
          show: true,
          orient: "vertical",
          left: "right",
          top: "center",
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            magicType: { show: true, type: ["line", "bar", "stack"] },
            restore: { show: true },
            saveAsImage: { show: true },
          },
        },
        yAxis: [
          {
            type: "category",
            // axisTick: { show: false },
            data: xAxisKeys,
          },
        ],
        xAxis: {
          type: "value",
        },

        series: seriesData,
      };

      option && myChart.setOption(option);
    });
  },
};
</script>
  
  <style>
</style>
  