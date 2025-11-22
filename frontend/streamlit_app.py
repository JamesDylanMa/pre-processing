"""
Streamlit frontend application
"""
import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.file_upload import FileUploadHandler
from backend.storage import StorageManager
from processing.parsers.pdf_parser import PDFParser
from processing.parsers.word_parser import WordParser
from processing.parsers.excel_parser import ExcelParser
from processing.parsers.ppt_parser import PPTParser
# Additional parsers will be imported conditionally
from processing.processors.document_ai import DocumentAIProcessor
from processing.processors.ensemble_processor import EnsembleProcessor
from processing.ollama_integration import OllamaProcessor
from processing.comparison import ResultComparator
from config import ALLOWED_EXTENSIONS, OUTPUT_FORMATS, OLLAMA_MODELS
from utils.file_utils import get_file_type


# Page configuration
st.set_page_config(
    page_title="문서 전처리 서비스",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'file_metadata' not in st.session_state:
    st.session_state.file_metadata = None
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []  # 여러 파일 처리 기록
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None


def main():
    st.title("📄 문서 전처리 서비스")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # Processing options
        st.subheader("처리 옵션")
        use_ensemble = st.checkbox("앙상블 처리 사용", value=True)
        use_comparison = st.checkbox("결과 비교 활성화", value=True)
        use_ollama = st.checkbox("Ollama AI 처리 사용", value=False)
        
        # Ollama settings
        if use_ollama:
            st.subheader("Ollama 설정")
            ollama_model = st.selectbox(
                "모델 선택",
                options=OLLAMA_MODELS["multimodal"] + OLLAMA_MODELS["text"],
                index=0
            )
        else:
            ollama_model = None
        
        # Output format
        st.subheader("출력 형식")
        output_format = st.selectbox("저장 형식", OUTPUT_FORMATS, index=0)
        
        st.markdown("---")
        st.info(f"권장 모델: {OLLAMA_MODELS['recommended']}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📤 파일 업로드", "🔄 처리 결과", "📊 비교 분석", "📥 다운로드"])
    
    with tab1:
        st.header("파일 업로드")
        
        # 성공 메시지 표시
        if 'last_success_message' in st.session_state and st.session_state.last_success_message:
            st.success(st.session_state.last_success_message)
            # 메시지를 한 번만 표시하고 제거
            del st.session_state.last_success_message
        
        # 삭제 성공 메시지 표시
        if 'delete_success_message' in st.session_state and st.session_state.delete_success_message:
            st.success(st.session_state.delete_success_message)
            del st.session_state.delete_success_message
        
        # 처리된 파일 리스트 표시
        if st.session_state.processed_files:
            st.subheader("📋 처리된 파일 목록")
            for idx, file_info in enumerate(st.session_state.processed_files):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    file_icon = "📄" if file_info["file_type"] == "pdf" else "📝" if file_info["file_type"] == "word" else "📊" if file_info["file_type"] == "excel" else "📑" if file_info["file_type"] == "powerpoint" else "📎"
                    st.write(f"{file_icon} **{file_info['file_name']}** ({file_info['file_type']})")
                with col2:
                    st.write(f"`{len(file_info['results'])}개 결과`")
                with col3:
                    if st.button("보기", key=f"view_{file_info['file_id']}"):
                        st.session_state.processing_results = file_info["results"]
                        st.session_state.file_metadata = file_info["metadata"]
                        st.session_state.current_file_id = file_info["file_id"]
                        st.rerun()
                with col4:
                    if st.button("🗑️ 삭제", key=f"delete_{file_info['file_id']}"):
                        try:
                            # 파일 삭제
                            upload_handler = FileUploadHandler()
                            # 메타데이터에서 session_id 추출
                            session_id = file_info["metadata"].get("session_id")
                            if not session_id:
                                # 파일 경로에서 세션 ID 추출 시도
                                file_path = Path(file_info["metadata"]["file_path"])
                                if file_path.parent.name != "uploads":
                                    session_id = file_path.parent.name
                            
                            deleted = upload_handler.delete_file(file_info["file_id"], session_id)
                            
                            # 결과 파일도 삭제
                            storage = StorageManager()
                            result_files = storage.get_results_for_file(file_info["file_id"])
                            for result_file in result_files:
                                try:
                                    result_file.unlink()
                                except:
                                    pass
                            
                            # 세션 상태에서 제거
                            st.session_state.processed_files.pop(idx)
                            
                            # 현재 선택된 파일이 삭제된 파일이면 초기화
                            if st.session_state.current_file_id == file_info["file_id"]:
                                if st.session_state.processed_files:
                                    # 다른 파일이 있으면 첫 번째 파일 선택
                                    first_file = st.session_state.processed_files[0]
                                    st.session_state.processing_results = first_file["results"]
                                    st.session_state.file_metadata = first_file["metadata"]
                                    st.session_state.current_file_id = first_file["file_id"]
                                else:
                                    st.session_state.processing_results = []
                                    st.session_state.file_metadata = None
                                    st.session_state.current_file_id = None
                            
                            st.session_state.delete_success_message = f"파일이 삭제되었습니다: {file_info['file_name']}"
                            st.rerun()
                        except Exception as e:
                            st.error(f"파일 삭제 중 오류 발생: {str(e)}")
                st.divider()
        
        uploaded_file = st.file_uploader(
            "문서 파일을 업로드하세요",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'png', 'jpg', 'jpeg'],
            help="지원 형식: PDF, Word, Excel, PowerPoint, 텍스트, 이미지",
            key="file_uploader"
        )
        
        # 새 파일이 업로드되었는지 확인 (이전 파일과 다른 경우)
        if uploaded_file is not None:
            current_file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if 'last_uploaded_file_key' not in st.session_state or st.session_state.last_uploaded_file_key != current_file_key:
                # 새 파일이므로 이전 처리 결과 초기화하지 않음 (여러 파일 처리 지원)
                st.session_state.last_uploaded_file_key = current_file_key
        
        if uploaded_file is not None:
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("파일명", uploaded_file.name)
            with col2:
                st.metric("파일 크기", f"{uploaded_file.size / 1024:.2f} KB")
            with col3:
                file_type = get_file_type(uploaded_file.name)
                st.metric("파일 형식", file_type or "알 수 없음")
            
            # Upload button
            if st.button("📤 파일 업로드 및 처리 시작", type="primary", key="upload_button"):
                try:
                    # Initialize handlers
                    upload_handler = FileUploadHandler()
                    storage = StorageManager()
                    
                    # 각 파일마다 고유한 세션 ID 생성
                    file_session_id = f"{st.session_state.session_id}_{datetime.now().strftime('%H%M%S%f')}"
                    
                    # Save uploaded file
                    with st.spinner("파일을 업로드 중..."):
                        metadata = upload_handler.save_uploaded_file(
                            uploaded_file, 
                            file_session_id
                        )
                    
                    # 현재 파일 메타데이터 저장
                    st.session_state.file_metadata = metadata
                    st.session_state.current_file_id = metadata["file_id"]
                    
                    # Process file
                    with st.spinner("파일을 처리 중..."):
                        results = []
                        file_path = metadata["file_path"]
                        file_type = metadata["file_type"]
                        
                        # Base processing with appropriate parser (pdfplumber)
                        parsers = {
                            'pdf': PDFParser(),
                            'word': WordParser(),
                            'excel': ExcelParser(),
                            'powerpoint': PPTParser()
                        }
                        parser = parsers.get(file_type)
                        if parser:
                            base_result = parser.parse(file_path)
                            base_result["processing_time"] = time.time()
                            base_result["processor"] = "base_parser_pdfplumber"
                            results.append(base_result)
                        
                        # Additional PDF parsers for comparison (PDF only)
                        if file_type == 'pdf':
                            # PyMuPDF parser (fast and accurate)
                            try:
                                from processing.parsers.pdf_pymupdf_parser import PyMuPDFParser
                                pymupdf_parser = PyMuPDFParser()
                                pymupdf_result = pymupdf_parser.parse(file_path)
                                if "error" not in pymupdf_result:
                                    pymupdf_result["processing_time"] = time.time()
                                    pymupdf_result["processor"] = "pymupdf_parser"
                                    results.append(pymupdf_result)
                            except ImportError:
                                pass
                            
                            # PDFMiner parser (good for text extraction)
                            try:
                                from processing.parsers.pdf_pdfminer_parser import PDFMinerParser
                                pdfminer_parser = PDFMinerParser()
                                pdfminer_result = pdfminer_parser.parse(file_path)
                                if "error" not in pdfminer_result:
                                    pdfminer_result["processing_time"] = time.time()
                                    pdfminer_result["processor"] = "pdfminer_parser"
                                    results.append(pdfminer_result)
                            except ImportError:
                                pass
                        
                        # AI processing
                        ai_processor = DocumentAIProcessor()
                        ai_result = ai_processor.process(file_path, file_type)
                        ai_result["processing_time"] = time.time()
                        results.append(ai_result)
                        
                        # Ensemble processing
                        if use_ensemble:
                            ensemble_processor = EnsembleProcessor()
                            ensemble_result = ensemble_processor.process(file_path, file_type)
                            ensemble_result["processing_time"] = time.time()
                            results.append(ensemble_result)
                        
                        # Additional PDF parsers for table extraction (PDF only)
                        if file_type == 'pdf':
                            # Camelot parser (table extraction)
                            try:
                                from processing.parsers.pdf_camelot_parser import CamelotParser
                                camelot_parser = CamelotParser()
                                camelot_result = camelot_parser.parse(file_path)
                                if "error" not in camelot_result:
                                    camelot_result["processing_time"] = time.time()
                                    camelot_result["processor"] = "camelot_parser"
                                    results.append(camelot_result)
                            except ImportError:
                                pass
                            
                            # Tabula parser (table extraction)
                            try:
                                from processing.parsers.pdf_tabula_parser import TabulaParser
                                tabula_parser = TabulaParser()
                                tabula_result = tabula_parser.parse(file_path)
                                if "error" not in tabula_result:
                                    tabula_result["processing_time"] = time.time()
                                    tabula_result["processor"] = "tabula_parser"
                                    results.append(tabula_result)
                            except ImportError:
                                pass
                        
                        # Ollama processing
                        if use_ollama and ollama_model:
                            ollama_processor = OllamaProcessor(ollama_model)
                            if ollama_processor.is_available():
                                ollama_result = ollama_processor.process_document(file_path, file_type)
                                if ollama_result and "error" not in ollama_result:
                                    ollama_result["processing_time"] = time.time()
                                    ollama_result["processor"] = f"ollama_{ollama_model}"
                                    results.append(ollama_result)
                            else:
                                st.warning("Ollama 서비스에 연결할 수 없습니다.")
                    
                    # Save results
                    with st.spinner("결과를 저장 중..."):
                        saved_files = []
                        original_filename = metadata.get("original_name", "")
                        for result in results:
                            # 프로세서 이름 우선순위: processor > parser > unknown
                            processor_name = result.get("processor") or result.get("parser") or "unknown"
                            saved_path = storage.save_result(
                                result,
                                metadata["file_id"],
                                processor_name,
                                output_format,
                                original_filename=original_filename
                            )
                            saved_files.append(saved_path)
                    
                    # 현재 파일의 처리 결과를 세션에 추가 (이전 결과 유지)
                    file_result = {
                        "file_id": metadata["file_id"],
                        "file_name": metadata["original_name"],
                        "file_type": metadata["file_type"],
                        "results": results,
                        "metadata": metadata
                    }
                    
                    # 같은 파일이 이미 처리되었는지 확인
                    existing_index = next(
                        (i for i, f in enumerate(st.session_state.processed_files) 
                         if f["file_id"] == metadata["file_id"]), 
                        None
                    )
                    
                    if existing_index is not None:
                        # 기존 파일 업데이트
                        st.session_state.processed_files[existing_index] = file_result
                    else:
                        # 새 파일 추가
                        st.session_state.processed_files.append(file_result)
                    
                    # 현재 파일의 결과를 processing_results에 설정
                    st.session_state.processing_results = results
                    
                    # 성공 메시지를 세션 상태에 저장 (rerun 후에도 표시되도록)
                    st.session_state.last_success_message = f"✅ 처리가 완료되었습니다! ({metadata['original_name']})"
                    st.session_state.last_processed_file_id = metadata["file_id"]
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with tab2:
        st.header("처리 결과")
        
        # 여러 파일이 처리된 경우 선택할 수 있도록
        if st.session_state.processed_files:
            if len(st.session_state.processed_files) > 1:
                file_options = [f"{f['file_name']} ({f['file_type']})" for f in st.session_state.processed_files]
                selected_file_index = st.selectbox(
                    "처리된 파일 선택",
                    options=range(len(st.session_state.processed_files)),
                    format_func=lambda x: file_options[x],
                    key="file_selector"
                )
                selected_file = st.session_state.processed_files[selected_file_index]
                st.session_state.processing_results = selected_file["results"]
                st.session_state.file_metadata = selected_file["metadata"]
                st.session_state.current_file_id = selected_file["file_id"]
            else:
                # 파일이 하나만 있는 경우
                selected_file = st.session_state.processed_files[0]
                st.session_state.processing_results = selected_file["results"]
                st.session_state.file_metadata = selected_file["metadata"]
                st.session_state.current_file_id = selected_file["file_id"]
        
        if st.session_state.processing_results:
            for i, result in enumerate(st.session_state.processing_results):
                # 프로세서 이름 우선순위: processor > parser > 기본값
                processor_name = result.get("processor") or result.get("parser") or f"Processor {i+1}"
                
                # 더 명확한 이름으로 변환
                name_mapping = {
                    "pdf_parser": "PDF Parser (pdfplumber)",
                    "pymupdf_parser": "PDF Parser (PyMuPDF)",
                    "pdfminer_parser": "PDF Parser (pdfminer)",
                    "camelot_parser": "PDF Parser (Camelot - Tables)",
                    "tabula_parser": "PDF Parser (Tabula - Tables)",
                    "document_ai": "Document AI Processor",
                    "ensemble_processor": "Ensemble Processor",
                    "base_parser_pdfplumber": "Base Parser (pdfplumber)",
                    "word_parser": "Word Parser",
                    "excel_parser": "Excel Parser",
                    "ppt_parser": "PowerPoint Parser"
                }
                # Ollama 프로세서 이름 처리
                if processor_name.startswith("ollama_"):
                    model_name = processor_name.replace("ollama_", "")
                    processor_name = f"Ollama AI ({model_name})"
                else:
                    processor_name = name_mapping.get(processor_name, processor_name)
                
                with st.expander(f"📋 {processor_name} 결과", expanded=(i == 0)):
                    # Display text content
                    if result.get("text"):
                        st.subheader("추출된 텍스트")
                        st.text_area(
                            "텍스트 내용",
                            value=result["text"][:5000] + ("..." if len(result["text"]) > 5000 else ""),
                            height=200,
                            disabled=True,
                            key=f"text_area_{i}_{processor_name}"
                        )
                    
                    # Display metadata
                    if result.get("metadata"):
                        st.subheader("메타데이터")
                        st.json(result["metadata"])
                    
                    # Display tables
                    if result.get("tables"):
                        st.subheader("추출된 테이블")
                        for j, table in enumerate(result["tables"][:3]):  # Show first 3 tables
                            st.dataframe(table.get("rows", []), key=f"table_{i}_{j}")
                    
                    # Display sheets (for Excel)
                    if result.get("sheets"):
                        st.subheader("시트 정보")
                        for k, sheet in enumerate(result["sheets"][:3]):  # Show first 3 sheets
                            st.write(f"**시트명**: {sheet['sheet_name']}")
                            if sheet.get("data"):
                                st.dataframe(sheet["data"][:100], key=f"sheet_{i}_{k}")  # Show first 100 rows
        else:
            st.info("처리된 결과가 없습니다. 파일을 업로드하고 처리해주세요.")
    
    with tab3:
        st.header("비교 분석")
        
        # 여러 파일이 처리된 경우 선택할 수 있도록
        if st.session_state.processed_files:
            if len(st.session_state.processed_files) > 1:
                file_options = [f"{f['file_name']} ({f['file_type']})" for f in st.session_state.processed_files]
                selected_file_index = st.selectbox(
                    "비교할 파일 선택",
                    options=range(len(st.session_state.processed_files)),
                    format_func=lambda x: file_options[x],
                    key="comparison_file_selector"
                )
                selected_file = st.session_state.processed_files[selected_file_index]
                comparison_results = selected_file["results"]
            else:
                comparison_results = st.session_state.processed_files[0]["results"]
        else:
            comparison_results = st.session_state.processing_results
        
        if len(comparison_results) > 1 and use_comparison:
            comparator = ResultComparator()
            comparison = comparator.compare_results(comparison_results)
            
            # Display comparison metrics
            st.subheader("처리기 비교 지표")
            if comparison.get("comparison_metrics"):
                import pandas as pd
                df = pd.DataFrame(comparison["comparison_metrics"])
                st.dataframe(df, key="comparison_metrics_df")
            
            # Display recommendations
            st.subheader("추천 사항")
            if comparison.get("recommendations"):
                for rec in comparison["recommendations"]:
                    st.info(rec)
            
            # Display best processor
            if comparison.get("best_processor"):
                st.subheader("최적 처리기")
                best = comparison["best_processor"]
                st.success(f"**{best['processor']}** (점수: {best['score']:.2f})")
                st.json(best["metrics"])
            
            # Save comparison result
            if st.button("비교 결과 저장", key="save_comparison_button"):
                storage = StorageManager()
                # 현재 선택된 파일의 ID 사용
                if st.session_state.processed_files:
                    if len(st.session_state.processed_files) > 1:
                        selected_file_index = st.session_state.get("comparison_file_selector", 0)
                        file_id = st.session_state.processed_files[selected_file_index]["file_id"]
                    else:
                        file_id = st.session_state.processed_files[0]["file_id"]
                elif st.session_state.file_metadata:
                    file_id = st.session_state.file_metadata["file_id"]
                else:
                    st.error("파일 정보를 찾을 수 없습니다.")
                    file_id = None
                
                if file_id:
                    saved_path = storage.save_comparison_result(
                        comparison,
                        file_id
                    )
                    st.success(f"비교 결과가 저장되었습니다: {saved_path.name}")
        else:
            st.info("비교를 위해 최소 2개 이상의 처리 결과가 필요합니다.")
    
    with tab4:
        st.header("다운로드")
        
        # 여러 파일이 처리된 경우 선택할 수 있도록
        if st.session_state.processed_files:
            if len(st.session_state.processed_files) > 1:
                file_options = [f"{f['file_name']} ({f['file_type']})" for f in st.session_state.processed_files]
                selected_file_index = st.selectbox(
                    "다운로드할 파일 선택",
                    options=range(len(st.session_state.processed_files)),
                    format_func=lambda x: file_options[x],
                    key="download_file_selector"
                )
                selected_file = st.session_state.processed_files[selected_file_index]
                file_id = selected_file["file_id"]
                file_name = selected_file["file_name"]
            else:
                file_id = st.session_state.processed_files[0]["file_id"]
                file_name = st.session_state.processed_files[0]["file_name"]
            
            storage = StorageManager()
            result_files = storage.get_results_for_file(file_id)
            
            if result_files:
                st.subheader(f"저장된 결과 파일: {file_name}")
                for result_file in result_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {result_file.name}")
                    with col2:
                        with open(result_file, "rb") as f:
                            st.download_button(
                                "다운로드",
                                f.read(),
                                file_name=result_file.name,
                                key=f"download_{file_id}_{result_file.name}",
                                mime="application/json" if result_file.suffix == ".json" else "text/markdown"
                            )
            else:
                st.info("다운로드할 파일이 없습니다.")
        elif st.session_state.file_metadata:
            # 기존 방식 호환성 유지
            storage = StorageManager()
            file_id = st.session_state.file_metadata["file_id"]
            result_files = storage.get_results_for_file(file_id)
            
            if result_files:
                st.subheader("저장된 결과 파일")
                for result_file in result_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {result_file.name}")
                    with col2:
                        with open(result_file, "rb") as f:
                            st.download_button(
                                "다운로드",
                                f.read(),
                                file_name=result_file.name,
                                key=f"download_{result_file.name}",
                                mime="application/json" if result_file.suffix == ".json" else "text/markdown"
                            )
            else:
                st.info("다운로드할 파일이 없습니다.")
        else:
            st.info("처리된 파일이 없습니다.")


if __name__ == "__main__":
    main()

