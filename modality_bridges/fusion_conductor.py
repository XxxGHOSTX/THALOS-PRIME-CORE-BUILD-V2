"""
Multi-Modal Fusion System
Custom bridges for heterogeneous data types
"""

import numpy as np
from datetime import datetime as dt


class TextBridge:
    """Bridge for text modality"""
    
    def __init__(self):
        self.proc_log = []
        
    def extract(self, txt_data):
        """Extract text features"""
        
        # Character analysis
        char_map = {}
        for ch in txt_data:
            char_map[ch] = char_map.get(ch, 0) + 1
            
        # Token analysis
        tokens = txt_data.lower().split()
        tok_cnt = len(tokens)
        avg_tok_len = np.mean([len(t) for t in tokens]) if tokens else 0
        
        # Semantic signals
        q_signals = sum(1 for t in ['what', 'when', 'where', 'why', 'how', 'who'] if t in tokens)
        pos_signals = sum(1 for t in ['good', 'great', 'excellent', 'happy'] if t in tokens)
        neg_signals = sum(1 for t in ['bad', 'terrible', 'sad', 'poor'] if t in tokens)
        
        feat = {
            'bridge': 'text',
            'char_cnt': len(txt_data),
            'token_cnt': tok_cnt,
            'avg_tok_len': float(avg_tok_len),
            'unique_chars': len(char_map),
            'question_sig': q_signals,
            'sentiment_sig': pos_signals - neg_signals,
            'ts': dt.now().isoformat()
        }
        
        self.proc_log.append(feat)
        return feat


class NumericBridge:
    """Bridge for numerical modality"""
    
    def __init__(self):
        self.proc_log = []
        
    def extract(self, num_data):
        """Extract numerical features"""
        
        if not num_data:
            return {'bridge': 'numeric', 'empty': True}
            
        arr = np.array(num_data)
        
        feat = {
            'bridge': 'numeric',
            'elements': len(num_data),
            'mean_val': float(np.mean(arr)),
            'std_val': float(np.std(arr)),
            'min_val': float(np.min(arr)),
            'max_val': float(np.max(arr)),
            'median_val': float(np.median(arr)),
            'ts': dt.now().isoformat()
        }
        
        self.proc_log.append(feat)
        return feat


class MetaBridge:
    """Bridge for metadata modality"""
    
    def __init__(self):
        self.proc_log = []
        
    def extract(self, meta_data):
        """Extract metadata features"""
        
        feat = {
            'bridge': 'metadata',
            'fields': len(meta_data),
            'field_keys': list(meta_data.keys()),
            'has_time': any(k in meta_data for k in ['time', 'timestamp', 'ts']),
            'has_loc': any(k in meta_data for k in ['location', 'pos', 'coords']),
            'ts': dt.now().isoformat()
        }
        
        self.proc_log.append(feat)
        return feat


class FusionConductor:
    """Conduct fusion across modalities"""
    
    def __init__(self):
        self.text_br = TextBridge()
        self.num_br = NumericBridge()
        self.meta_br = MetaBridge()
        self.fusion_log = []
        
    def conduct_fusion(self, data_bundle):
        """
        Fuse multiple modality inputs
        
        Args:
            data_bundle: Dict with 'text', 'numeric', 'metadata' keys
        """
        
        fusion_result = {
            'ts': dt.now().isoformat(),
            'modalities': [],
            'features': {}
        }
        
        # Extract from each modality
        if 'text' in data_bundle and data_bundle['text']:
            txt_feat = self.text_br.extract(data_bundle['text'])
            fusion_result['features']['text'] = txt_feat
            fusion_result['modalities'].append('text')
            
        if 'numeric' in data_bundle and data_bundle['numeric']:
            num_feat = self.num_br.extract(data_bundle['numeric'])
            fusion_result['features']['numeric'] = num_feat
            fusion_result['modalities'].append('numeric')
            
        if 'metadata' in data_bundle and data_bundle['metadata']:
            meta_feat = self.meta_br.extract(data_bundle['metadata'])
            fusion_result['features']['metadata'] = meta_feat
            fusion_result['modalities'].append('metadata')
            
        # Create fusion vector
        fusion_result['fusion_vec'] = self._create_fusion_vector(fusion_result['features'])
        
        self.fusion_log.append(fusion_result)
        
        return fusion_result
    
    def _create_fusion_vector(self, feat_map):
        """Create unified vector from features"""
        
        vec = []
        
        # Text contributions
        if 'text' in feat_map:
            tf = feat_map['text']
            vec.extend([
                tf.get('char_cnt', 0) / 1000.0,
                tf.get('token_cnt', 0) / 100.0,
                tf.get('avg_tok_len', 0) / 10.0,
                tf.get('question_sig', 0) / 10.0,
                tf.get('sentiment_sig', 0) / 10.0
            ])
        else:
            vec.extend([0.0] * 5)
            
        # Numeric contributions
        if 'numeric' in feat_map:
            nf = feat_map['numeric']
            if not nf.get('empty', False):
                vec.extend([
                    nf.get('mean_val', 0),
                    nf.get('std_val', 0),
                    nf.get('median_val', 0)
                ])
            else:
                vec.extend([0.0] * 3)
        else:
            vec.extend([0.0] * 3)
            
        # Metadata contributions
        if 'metadata' in feat_map:
            mf = feat_map['metadata']
            vec.extend([
                mf.get('fields', 0) / 10.0,
                1.0 if mf.get('has_time', False) else 0.0,
                1.0 if mf.get('has_loc', False) else 0.0
            ])
        else:
            vec.extend([0.0] * 3)
            
        return vec
    
    def conductor_metrics(self):
        """Get conductor metrics"""
        
        return {
            'fusions': len(self.fusion_log),
            'text_processed': len(self.text_br.proc_log),
            'numeric_processed': len(self.num_br.proc_log),
            'metadata_processed': len(self.meta_br.proc_log)
        }
