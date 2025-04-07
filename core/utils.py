import logging
import os
import json
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(filename='hyperscan.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def save_results(results, output_dir="results", format="txt"):
    """حفظ النتائج بتنسيق TXT أو JSON"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if format == "json":
        filename = os.path.join(output_dir, f"scan_results_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    else:
        filename = os.path.join(output_dir, f"scan_results_{timestamp}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join([str(r) for r in results]))
    return filename

def clean_cache():
    """تنظيف الملفات المؤقتة"""
    import shutil
    shutil.rmtree('__pycache__', ignore_errors=True)
    logging.info("Cache cleaned")
