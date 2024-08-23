import os
import clang.cindex

# Initialize the clang index
clang.cindex.Config.set_library_file('/path/to/your/clang/libclang.so')  # libclang 경로를 설정

def parse_cpp_header(header_file):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(header_file, args=['-std=c++17'])  # C++17 표준으로 파싱

    structs = {}
    
    def visit_node(node):
        if node.kind == clang.cindex.CursorKind.STRUCT_DECL:
            struct_name = node.spelling
            fields = []
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.FIELD_DECL:
                    field_name = child.spelling
                    field_type = child.type.spelling
                    fields.append((field_name, field_type))
            structs[struct_name] = fields

        for child in node.get_children():
            visit_node(child)

    visit_node(translation_unit.cursor)
    return structs

def generate_ctypes_code(structs):
    code = "import ctypes\n\n"
    for struct_name, fields in structs.items():
        code += f"class {struct_name}(ctypes.Structure):\n"
        code += "    _fields_ = [\n"
        for field_name, field_type in fields:
            # 여기서 C++ 타입을 ctypes 타입으로 매핑해야 합니다.
            ctype = {
                'int': 'ctypes.c_int',
                'float': 'ctypes.c_float',
                'double': 'ctypes.c_double',
                'char': 'ctypes.c_char',
                'bool': 'ctypes.c_bool'
            }.get(field_type, 'ctypes.c_void_p')  # 기본값으로 void pointer 사용
            code += f"        ('{field_name}', {ctype}),\n"
        code += "    ]\n\n"
    return code

def process_headers_in_directory(directory):
    all_structs = {}
    for root, _, files in os.walk(directory):  # 디렉토리 내 모든 파일 검색
        for file in files:
            if file.endswith(".h"):  # .h 파일만 처리
                file_path = os.path.join(root, file)
                print(f"Parsing {file_path}...")
                structs = parse_cpp_header(file_path)
                all_structs.update(structs)
    return generate_ctypes_code(all_structs)

# 현재 스크립트의 디렉토리 경로를 가져옴
root_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = root_dir + '/dgnlib/'

# Python ctypes 구조체 코드 생성
generated_code = process_headers_in_directory(root_dir)

# 생성된 코드를 출력하거나 파일에 저장
output_file = os.path.join(root_dir, "generated_structs.py")
with open(output_file, "w") as f:
    f.write(generated_code)

print(f"Generated Python code saved to {output_file}")