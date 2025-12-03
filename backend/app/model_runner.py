# app/model_runner.py

import datetime
import json
from typing import Dict, Any, List

from .ai_models import MODEL_REGISTRY
from .db import get_session
from .models import InferenceResult


def run_models_for_frame(
    stream_id: int,
    frame,
    enabled_model_names: List[str],
) -> List[Dict[str, Any]]:
    """
    Run all enabled models for a given frame and stream_id.
    Save results into the DB and return them as a list.
    This is a generic utility, not used directly by StreamWorker right now.
    """

    session = get_session()
    results: List[Dict[str, Any]] = []

    try:
        for model_name in enabled_model_names:
            ModelCls = MODEL_REGISTRY.get(model_name)
            if not ModelCls:
                print(f"[model_runner] Unknown model {model_name}, skipping")
                continue

            model = ModelCls()
            try:
                prediction = model.predict(frame)
            except Exception as e:
                print(f"[model_runner] Error running model {model_name}: {e}")
                continue

            # store in DB
            ir = InferenceResult(
                stream_id=stream_id,
                model_name=model_name,
                timestamp=datetime.datetime.utcnow(),
                result_json=json.dumps(prediction),
            )
            session.add(ir)
            session.commit()

            results.append(
                {
                    "stream_id": stream_id,
                    "model": model_name,
                    "result": prediction,
                    "timestamp": ir.timestamp.isoformat(),
                }
            )

    finally:
        session.close()

    return results
