import subprocess

def run_node_script(encoded_xml, address='./bundle.js'):
    # Node.js 스크립트를 실행하기 위한 명령어와 인자 설정
    command = ['node', address , encoded_xml]

    # decoded_xml = base64.b64decode(encoded_xml).decode('utf-8')

    try:
        # subprocess.run을 사용하여 Node.js 스크립트를 실행하고 결과를 캡처
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # 표준 출력 결과 반환
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 에러 발생 시 에러 메시지 출력
        print(f"Error occurred: {e.stderr}")
        return None


# 예제 실행
# if __name__ == "__main__":
#     a = 5
#     b = 3
#     xmlString = '<?xml version="1.0" encoding="utf-8"?><SHEET Version="" RatioId="1X1" TemplateName="" LayoutId="" IsFreeStyle="true" Page="1"><SHEETSIZE cx="500" cy="500"/><TEMPLATE Width="500" Height="500"/><BACKGROUND Color="#ffffff"><PureSkinSize cx="" cy=""/><CropRect Left="0" Top="0" Right="0" Bottom="0"/></BACKGROUND><TEXT Rotate="0" Opacity="255" FlipH="0" FlipV="0" AddedBy="0" TbpeId="text1542952880170ASCXD6WFWV" GroupId="" Priority="0" BackgroundColor="00000000" FillBackground="false" Alignment="2" VAlignment="0" UpperCase="false"><Position Left="-15" Top="406" Right="512" Bottom="452"/><TEMPLATE CanUserSelect="-1" CanUserMove="-1" CanUserResize="-1" CanUserDel="-1"/><Text>Fantasy House</Text><TextData>[{"a":1,"s":0,"c":[{"t":"Fantasy House","c":"#2E2E2F","z":15.823180389636326,"f":0,"da":true,"dx":90,"ds":110,"oa":false,"ol":0,"oc":"#000000","op":"","oz":0,"sa":false,"sl":0,"sg":180,"sc":"#000000","sd":0,"sp":"","sz":1,"sr":0,"yb":false,"yf":"Gill Sans MT","yi":false,"yu":false,"yt":false}]}]</TextData><Font Color="FF2E2E2F" Family="Gill Sans MT" Size="15.823180389636326" LineSpace="0"><Style Bold="false" Italic="false" Strikeout="false" Underline="false"/></Font><Effect BezierPercent="0" TextSpace="11" ScaleX="0.9"><Outline DoOutline="false" Color="0000000" Size="0"/><Shadow DoShadow="false" Color="0000000" Distance="0" Angle="180" Spread="NaN"/><Fill Type="Color"/></Effect></TEXT><TEXT Rotate="0" Opacity="255" FlipH="0" FlipV="0" AddedBy="0" TbpeId="text15429528801711SAXQ48JBD" GroupId="" Priority="1" BackgroundColor="00000000" FillBackground="false" Alignment="2" VAlignment="0" UpperCase="false"><Position Left="205" Top="178" Right="296" Bottom="329"/><TEMPLATE CanUserSelect="-1" CanUserMove="-1" CanUserResize="-1" CanUserDel="-1"/><Text>F</Text><TextData>[{"a":1,"s":0,"c":[{"t":"F","c":"#2E2E2F","z":90,"f":0,"da":true,"dx":100,"ds":0,"oa":false,"ol":0,"oc":"#000000","op":"","oz":0,"sa":false,"sl":0,"sg":180,"sc":"#000000","sd":0,"sp":"","sz":1,"sr":0,"yb":false,"yf":"Pistilli","yi":false,"yu":false,"yt":false}]}]</TextData><Font Color="FF2E2E2F" Family="Pistilli" Size="90" LineSpace="0"><Style Bold="false" Italic="false" Strikeout="false" Underline="false"/></Font><Effect BezierPercent="0" TextSpace="0" ScaleX="1"><Outline DoOutline="false" Color="0000000" Size="0"/><Shadow DoShadow="false" Color="0000000" Distance="0" Angle="180" Spread="NaN"/><Fill Type="Color"/></Effect></TEXT><SVG Rotate="0" Opacity="255" FlipH="0" FlipV="0" AddedBy="0" TbpeId="1542952915894-VL78U8BWPS" GroupId="" Priority="2" SvgKey="2d739633-bd87-4d65-b396-33bd872d656f" IsBackground="false"><Position Left="84" Top="62" Right="418" Bottom="395"/><TEMPLATE CanUserSelect="-1" CanUserMove="-1" CanUserResize="-1" CanUserDel="-1"/><fillColorMap><fillColor originColor="#d91d5e" color="#d91d5e"/></fillColorMap><SvgLayer layerId="90MGSSONSQ" left="0" top="0" scaleX="1" scaleY="1" scaleCommon="4.0047275517817855"/></SVG></SHEET>'
#     output = run_node_script(a, b, '../bundle.js', xmlString)
#     if output:
#         print(f"Output from Node.js script:\n{output}")