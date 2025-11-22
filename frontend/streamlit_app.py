"""
Streamlit frontend application
"""
import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import json
import zipfile
from io import BytesIO

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

# Initialize comparator for scoring
comparator = ResultComparator()


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


def process_single_file(uploaded_file, upload_handler, storage, file_session_id, 
                       use_ensemble, use_ollama, ollama_model, output_format):
    """단일 파일 처리 함수"""
    # Save uploaded file
    metadata = upload_handler.save_uploaded_file(uploaded_file, file_session_id)
    
    # Process file
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
        except (ImportError, Exception):
            pass
        
        # pypdf parser (modern PyPDF2 successor)
        try:
            from processing.parsers.pdf_pypdf_parser import PyPDFParser
            pypdf_parser = PyPDFParser()
            pypdf_result = pypdf_parser.parse(file_path)
            if "error" not in pypdf_result:
                pypdf_result["processing_time"] = time.time()
                pypdf_result["processor"] = "pypdf_parser"
                results.append(pypdf_result)
        except (ImportError, Exception):
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
    
    # Additional PDF parsers for table extraction (PDF only) - Optional
    if file_type == 'pdf':
        # Camelot parser (table extraction) - requires Java and OpenCV
        try:
            from processing.parsers.pdf_camelot_parser import CamelotParser
            camelot_parser = CamelotParser()
            camelot_result = camelot_parser.parse(file_path)
            if "error" not in camelot_result and camelot_result.get("tables"):
                camelot_result["processing_time"] = time.time()
                camelot_result["processor"] = "camelot_parser"
                results.append(camelot_result)
        except (ImportError, Exception) as e:
            pass
        
        # Tabula parser (table extraction) - requires Java
        try:
            from processing.parsers.pdf_tabula_parser import TabulaParser
            tabula_parser = TabulaParser()
            tabula_result = tabula_parser.parse(file_path)
            if "error" not in tabula_result and tabula_result.get("tables"):
                tabula_result["processing_time"] = time.time()
                tabula_result["processor"] = "tabula_parser"
                results.append(tabula_result)
        except (ImportError, Exception) as e:
            pass
        
        # EasyOCR parser (better OCR alternative, no external dependencies)
        try:
            from processing.parsers.pdf_easyocr_parser import EasyOCRParser
            easyocr_parser = EasyOCRParser()
            if easyocr_parser.reader is not None:  # Only use if reader initialized successfully
                easyocr_result = easyocr_parser.parse(file_path)
                if "error" not in easyocr_result and (easyocr_result.get("text") or easyocr_result.get("pages")):
                easyocr_result["processing_time"] = time.time()
                easyocr_result["processor"] = "easyocr_parser"
                results.append(easyocr_result)
        except (ImportError, Exception) as e:
            pass
        
        # OCR parser (for scanned PDFs) - requires Tesseract (fallback)
        try:
            from processing.parsers.pdf_ocr_parser import OCRParser
            ocr_parser = OCRParser()
            ocr_result = ocr_parser.parse(file_path)
            if "error" not in ocr_result:
                ocr_result["processing_time"] = time.time()
                ocr_result["processor"] = "ocr_parser"
                results.append(ocr_result)
        except (ImportError, Exception) as e:
            pass
        
        # Unstructured parser (advanced document structure extraction)
        try:
            from processing.parsers.pdf_unstructured_parser import UnstructuredParser
            unstructured_parser = UnstructuredParser()
            unstructured_result = unstructured_parser.parse(file_path)
            if "error" not in unstructured_result:
                unstructured_result["processing_time"] = time.time()
                unstructured_result["processor"] = "unstructured_parser"
                results.append(unstructured_result)
        except (ImportError, Exception) as e:
            pass
        
        # PDFQuery parser (CSS-like selectors for structured PDFs)
        try:
            from processing.parsers.pdf_pdfquery_parser import PDFQueryParser
            pdfquery_parser = PDFQueryParser()
            pdfquery_result = pdfquery_parser.parse(file_path)
            if "error" not in pdfquery_result:
                pdfquery_result["processing_time"] = time.time()
                pdfquery_result["processor"] = "pdfquery_parser"
                results.append(pdfquery_result)
        except (ImportError, Exception) as e:
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
    
    # Filter out results with errors or empty results
    valid_results = [r for r in results if "error" not in r and (r.get("text") or r.get("tables") or r.get("pages") or r.get("metadata"))]
    
    # Score and sort results by quality
    sorted_results = comparator.score_and_sort_results(valid_results)
    
    # Save results
    saved_files = []
    original_filename = metadata.get("original_name", "")
    for result in sorted_results:
        processor_name = result.get("processor") or result.get("parser")
        if not processor_name:
            continue  # Skip results without processor name
        saved_path = storage.save_result(
            result,
            metadata["file_id"],
            processor_name,
            output_format,
            original_filename=original_filename
        )
        saved_files.append(saved_path)
    
    # 파일 결과 반환 (점수 순으로 정렬된 결과)
    file_result = {
        "file_id": metadata["file_id"],
        "file_name": metadata["original_name"],
        "file_type": metadata["file_type"],
        "results": sorted_results,  # 점수 순으로 정렬된 결과
        "metadata": metadata
    }
    
    return file_result


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
                            upload_handler = FileUploadHandler()
                            session_id = file_info["metadata"].get("session_id")
                            if not session_id:
                                file_path = Path(file_info["metadata"]["file_path"])
                                if file_path.parent.name != "uploads":
                                    session_id = file_path.parent.name
                            
                            upload_handler.delete_file(file_info["file_id"], session_id)
                            
                            storage = StorageManager()
                            result_files = storage.get_results_for_file(file_info["file_id"])
                            for result_file in result_files:
                                try:
                                    result_file.unlink()
                                except:
                                    pass
                            
                            st.session_state.processed_files.pop(idx)
                            
                            if st.session_state.current_file_id == file_info["file_id"]:
                                if st.session_state.processed_files:
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
        
        # 여러 파일 업로드 지원
        uploaded_files = st.file_uploader(
            "문서 파일을 업로드하세요 (여러 파일 선택 가능)",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'png', 'jpg', 'jpeg'],
            help="지원 형식: PDF, Word, Excel, PowerPoint, 텍스트, 이미지. 여러 파일을 동시에 선택할 수 있습니다.",
            key="file_uploader",
            accept_multiple_files=True
        )
        
        # 업로드된 파일 목록 표시
        if uploaded_files and len(uploaded_files) > 0:
            st.subheader(f"📎 선택된 파일 ({len(uploaded_files)}개)")
            for idx, file in enumerate(uploaded_files):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    file_icon = "📄" if file.name.lower().endswith('.pdf') else "📝" if file.name.lower().endswith(('.doc', '.docx')) else "📊" if file.name.lower().endswith(('.xls', '.xlsx')) else "📑" if file.name.lower().endswith(('.ppt', '.pptx')) else "📎"
                    st.write(f"{file_icon} **{file.name}** ({file.size / 1024:.2f} KB)")
                with col2:
                    file_type = get_file_type(file.name)
                    st.write(f"`{file_type or '알 수 없음'}`")
                with col3:
                    st.write("✅ 준비됨")
        
        if uploaded_files and len(uploaded_files) > 0:
            # Upload button
            if st.button(f"📤 {len(uploaded_files)}개 파일 업로드 및 처리 시작", type="primary", key="upload_button"):
                try:
                    upload_handler = FileUploadHandler()
                    storage = StorageManager()
                    
                    processed_count = 0
                    failed_files = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for file_idx, uploaded_file in enumerate(uploaded_files):
                        try:
                            status_text.text(f"처리 중: {uploaded_file.name} ({file_idx + 1}/{len(uploaded_files)})")
                            progress_bar.progress((file_idx) / len(uploaded_files))
                            
                            file_session_id = f"{st.session_state.session_id}_{datetime.now().strftime('%H%M%S%f')}"
                            
                            # 파일 처리
                            file_result = process_single_file(
                                uploaded_file, upload_handler, storage, file_session_id,
                                use_ensemble, use_ollama, ollama_model, output_format
                            )
                            
                            # 세션 상태에 추가
                            existing_index = next(
                                (i for i, f in enumerate(st.session_state.processed_files) 
                                 if f["file_id"] == file_result["file_id"]), 
                                None
                            )
                            
                            if existing_index is not None:
                                st.session_state.processed_files[existing_index] = file_result
                            else:
                                st.session_state.processed_files.append(file_result)
                            
                            processed_count += 1
                            
                        except Exception as e:
                            failed_files.append((uploaded_file.name, str(e)))
                    
                    progress_bar.progress(1.0)
                    status_text.empty()
                    
                    # 성공 메시지
                    if processed_count > 0:
                        st.session_state.last_success_message = f"✅ {processed_count}개 파일 처리가 완료되었습니다!"
                        if failed_files:
                            st.session_state.last_success_message += f" ({len(failed_files)}개 실패)"
                    
                    # 실패한 파일 표시
                    if failed_files:
                        for file_name, error in failed_files:
                            st.error(f"❌ {file_name}: {error}")
                    
                    # 마지막 처리된 파일을 현재 파일로 설정
                    if st.session_state.processed_files:
                        last_file = st.session_state.processed_files[-1]
                        st.session_state.processing_results = last_file["results"]
                        st.session_state.file_metadata = last_file["metadata"]
                        st.session_state.current_file_id = last_file["file_id"]
                    
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
                selected_file = st.session_state.processed_files[0]
                st.session_state.processing_results = selected_file["results"]
                st.session_state.file_metadata = selected_file["metadata"]
                st.session_state.current_file_id = selected_file["file_id"]
        
        if st.session_state.processing_results:
            # 에러가 있는 결과 필터링
            valid_results = [r for r in st.session_state.processing_results 
                           if "error" not in r and (r.get("text") or r.get("tables") or r.get("pages") or r.get("metadata"))]
            
            if not valid_results:
                st.warning("유효한 처리 결과가 없습니다. 파일을 다시 업로드해주세요.")
                return
            
            # 점수 순으로 정렬된 결과 표시
            sorted_display_results = comparator.score_and_sort_results(valid_results)
            
            for i, result in enumerate(sorted_display_results):
                processor_name = result.get("processor") or result.get("parser")
                if not processor_name:
                    continue  # 프로세서 이름이 없는 결과는 건너뛰기
                
                name_mapping = {
                    "pdf_parser": "PDF Parser (pdfplumber)",
                    "pymupdf_parser": "PDF Parser (PyMuPDF)",
                    "pdfminer_parser": "PDF Parser (pdfminer)",
                    "pypdf_parser": "PDF Parser (pypdf)",
                    "easyocr_parser": "PDF Parser (EasyOCR - Better OCR)",
                    "ocr_parser": "PDF Parser (OCR - Tesseract)",
                    "unstructured_parser": "PDF Parser (Unstructured - Advanced)",
                    "pdfquery_parser": "PDF Parser (PDFQuery - CSS Selectors)",
                    "camelot_parser": "PDF Parser (Camelot - Tables)",
                    "tabula_parser": "PDF Parser (Tabula - Tables)",
                    "document_ai": "Document AI Processor",
                    "ensemble_processor": "Ensemble Processor",
                    "base_parser_pdfplumber": "Base Parser (pdfplumber)",
                    "word_parser": "Word Parser",
                    "excel_parser": "Excel Parser",
                    "ppt_parser": "PowerPoint Parser"
                }
                if processor_name.startswith("ollama_"):
                    model_name = processor_name.replace("ollama_", "")
                    processor_name = f"Ollama AI ({model_name})"
                else:
                    processor_name = name_mapping.get(processor_name, processor_name)
                
                with st.expander(f"📋 {processor_name} 결과", expanded=(i == 0)):
                    if result.get("text"):
                        st.subheader("추출된 텍스트")
                        st.text_area(
                            "텍스트 내용",
                            value=result["text"][:5000] + ("..." if len(result["text"]) > 5000 else ""),
                            height=200,
                            disabled=True,
                            key=f"text_area_{i}_{processor_name}"
                        )
                    
                    if result.get("metadata"):
                        st.subheader("메타데이터")
                        st.json(result["metadata"])
                    
                    if result.get("tables"):
                        st.subheader("추출된 테이블")
                        for j, table in enumerate(result["tables"][:3]):
                            st.dataframe(table.get("rows", []), key=f"table_{i}_{j}")
                    
                    if result.get("sheets"):
                        st.subheader("시트 정보")
                        for k, sheet in enumerate(result["sheets"][:3]):
                            st.write(f"**시트명**: {sheet['sheet_name']}")
                            if sheet.get("data"):
                                st.dataframe(sheet["data"][:100], key=f"sheet_{i}_{k}")
        else:
            st.info("처리된 결과가 없습니다. 파일을 업로드하고 처리해주세요.")
    
    with tab3:
        st.header("비교 분석")
        
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
            comparison = comparator.compare_results(comparison_results)
            
            if comparison.get("comparison_metrics"):
                import pandas as pd
                df = pd.DataFrame(comparison["comparison_metrics"])
                st.dataframe(df, key="comparison_metrics_df")
            
            if comparison.get("recommendations"):
                st.subheader("추천 사항")
                for rec in comparison["recommendations"]:
                    st.info(rec)
            
            if comparison.get("best_processor"):
                st.subheader("최적 처리기")
                best = comparison["best_processor"]
                st.success(f"**{best['processor']}** (점수: {best['score']:.2f})")
                st.json(best["metrics"])
            
            if st.button("비교 결과 저장", key="save_comparison_button"):
                storage = StorageManager()
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
                    saved_path = storage.save_comparison_result(comparison, file_id)
                    st.success(f"비교 결과가 저장되었습니다: {saved_path.name}")
        else:
            st.info("비교를 위해 최소 2개 이상의 처리 결과가 필요합니다.")
    
    with tab4:
        st.header("다운로드")
        
        storage = StorageManager()
        
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
                processing_results = selected_file["results"]
            else:
                file_id = st.session_state.processed_files[0]["file_id"]
                file_name = st.session_state.processed_files[0]["file_name"]
                processing_results = st.session_state.processed_files[0]["results"]
            
            result_files = storage.get_results_for_file(file_id)
            
            if processing_results:
                st.subheader(f"📦 {file_name} - 처리 결과 다운로드")
                
                # 파일별로 정리된 다운로드
                base_filename = Path(file_name).stem
                safe_base_name = "".join(c for c in base_filename if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                
                # 프로세서 이름 매핑
                name_mapping = {
                    "pdf_parser": "pdfplumber",
                    "pymupdf_parser": "pymupdf",
                    "pdfminer_parser": "pdfminer",
                    "pypdf_parser": "pypdf",
                    "easyocr_parser": "easyocr",
                    "ocr_parser": "ocr_tesseract",
                    "unstructured_parser": "unstructured",
                    "pdfquery_parser": "pdfquery",
                    "camelot_parser": "camelot",
                    "tabula_parser": "tabula",
                    "document_ai": "document_ai",
                    "ensemble_processor": "ensemble",
                    "base_parser_pdfplumber": "base_pdfplumber",
                    "word_parser": "word",
                    "excel_parser": "excel",
                    "ppt_parser": "powerpoint"
                }
                
                # 점수 순으로 정렬된 결과 사용
                sorted_results = comparator.score_and_sort_results(processing_results)
                
                # 개별 파일 다운로드 (점수 높은 순서대로)
                st.write("**개별 결과 다운로드 (점수 순):**")
                for i, result in enumerate(sorted_results):
                    processor_name = result.get("processor") or result.get("parser") or f"processor_{i+1}"
                    
                    if processor_name.startswith("ollama_"):
                        safe_name = processor_name.replace("ollama_", "ollama_")
                    else:
                        safe_name = name_mapping.get(processor_name, processor_name.replace(" ", "_").lower())
                    
                    display_name = name_mapping.get(processor_name, processor_name)
                    if processor_name.startswith("ollama_"):
                        display_name = f"Ollama ({processor_name.replace('ollama_', '')})"
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"• {display_name}")
                    with col2:
                        json_data = json.dumps(result, ensure_ascii=False, indent=2)
                        json_bytes = json_data.encode('utf-8')
                        st.download_button(
                            "📥 JSON",
                            json_bytes,
                            file_name=f"{safe_base_name}_{safe_name}.json",
                            key=f"json_download_{file_id}_{i}",
                            mime="application/json"
                        )
                    with col3:
                        md_content = storage._dict_to_markdown(result)
                        md_bytes = md_content.encode('utf-8')
                        st.download_button(
                            "📥 MD",
                            md_bytes,
                            file_name=f"{safe_base_name}_{safe_name}.md",
                            key=f"md_download_{file_id}_{i}",
                            mime="text/markdown"
                        )
                
                st.divider()
                
                # 파일별 ZIP 다운로드 (모든 결과를 하나의 ZIP으로, 점수 순)
                st.write("**전체 결과 ZIP 다운로드 (점수 순):**")
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # JSON 파일들 추가 (점수 높은 순서대로)
                    for i, result in enumerate(sorted_results):
                        processor_name = result.get("processor") or result.get("parser") or f"processor_{i+1}"
                        if processor_name.startswith("ollama_"):
                            safe_name = processor_name.replace("ollama_", "ollama_")
                        else:
                            safe_name = name_mapping.get(processor_name, processor_name.replace(" ", "_").lower())
                        
                        json_data = json.dumps(result, ensure_ascii=False, indent=2)
                        zip_file.writestr(f"{safe_base_name}_{safe_name}.json", json_data.encode('utf-8'))
                        
                        md_content = storage._dict_to_markdown(result)
                        zip_file.writestr(f"{safe_base_name}_{safe_name}.md", md_content.encode('utf-8'))
                
                zip_buffer.seek(0)
                st.download_button(
                    "📦 전체 결과 ZIP 다운로드 (JSON + MD)",
                    zip_buffer.getvalue(),
                    file_name=f"{safe_base_name}_all_results.zip",
                    key=f"zip_download_{file_id}",
                    mime="application/zip"
                )
                
                # 저장된 파일도 표시
                if result_files:
                    st.divider()
                    st.subheader(f"저장된 파일: {file_name}")
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
                                    key=f"download_saved_{file_id}_{result_file.name}",
                                    mime="application/json" if result_file.suffix == ".json" else "text/markdown"
                                )
            elif result_files:
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
                st.info("다운로드할 파일이 없습니다. 먼저 파일을 업로드하고 처리해주세요.")
        
        elif st.session_state.processing_results:
            file_name = st.session_state.file_metadata.get("original_name", "unknown") if st.session_state.file_metadata else "unknown"
            st.subheader("처리 결과 다운로드")
            
            base_filename = Path(file_name).stem
            safe_base_name = "".join(c for c in base_filename if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            
            name_mapping = {
                "pdf_parser": "pdfplumber",
                "pymupdf_parser": "pymupdf",
                "pdfminer_parser": "pdfminer",
                "pypdf_parser": "pypdf",
                "easyocr_parser": "easyocr",
                "ocr_parser": "ocr_tesseract",
                "unstructured_parser": "unstructured",
                "pdfquery_parser": "pdfquery",
                "camelot_parser": "camelot",
                "tabula_parser": "tabula",
                "document_ai": "document_ai",
                "ensemble_processor": "ensemble",
                "base_parser_pdfplumber": "base_pdfplumber"
            }
            
            # 점수 순으로 정렬
            sorted_results = comparator.score_and_sort_results(st.session_state.processing_results)
            
            for i, result in enumerate(sorted_results):
                processor_name = result.get("processor") or result.get("parser") or f"Processor_{i+1}"
                safe_name = name_mapping.get(processor_name, processor_name.replace(" ", "_").lower())
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{processor_name}**")
                with col2:
                    json_data = json.dumps(result, ensure_ascii=False, indent=2)
                    json_bytes = json_data.encode('utf-8')
                    st.download_button(
                        "📥 JSON",
                        json_bytes,
                        file_name=f"{safe_base_name}_{safe_name}.json",
                        key=f"json_download_direct_{i}",
                        mime="application/json"
                    )
                with col3:
                    md_content = storage._dict_to_markdown(result)
                    md_bytes = md_content.encode('utf-8')
                    st.download_button(
                        "📥 MD",
                        md_bytes,
                        file_name=f"{safe_base_name}_{safe_name}.md",
                        key=f"md_download_direct_{i}",
                        mime="text/markdown"
                    )
                st.divider()
        
        elif st.session_state.file_metadata:
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
                st.info("다운로드할 파일이 없습니다. 먼저 파일을 업로드하고 처리해주세요.")
        else:
            st.info("처리된 파일이 없습니다. 파일 업로드 탭에서 파일을 업로드하고 처리해주세요.")


if __name__ == "__main__":
    main()
