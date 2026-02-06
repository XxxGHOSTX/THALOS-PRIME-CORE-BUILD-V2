"""
Cognitive Inference System
Dynamic rule-based reasoning with pattern matching
"""

from datetime import datetime as dt


class InferenceRule:
    """Single inference rule"""
    
    def __init__(self, rule_name, cond_fn, act_fn, weight=0):
        self.rule_name = rule_name
        self.cond_fn = cond_fn
        self.act_fn = act_fn
        self.weight = weight
        self.fire_cnt = 0
        
    def test_condition(self, ctx):
        """Test if condition matches"""
        return self.cond_fn(ctx)
    
    def apply_action(self, ctx):
        """Apply rule action"""
        self.fire_cnt += 1
        return self.act_fn(ctx)


class CognitiveInferenceNet:
    """Dynamic reasoning network"""
    
    def __init__(self):
        self.rules = []
        self.inference_log = []
        self._init_base_rules()
        
    def _init_base_rules(self):
        """Initialize base reasoning rules"""
        
        # Greeting inference
        self.append_rule(
            'greet_detect',
            lambda c: any(w in c.get('q', '').lower() for w in ['hello', 'hi', 'hey', 'greetings']),
            lambda c: {'type': 'greeting', 'mood': 'friendly', 'act': 'greet_back'},
            weight=10
        )
        
        # Query inference
        self.append_rule(
            'query_detect',
            lambda c: any(w in c.get('q', '').lower() for w in ['what', 'when', 'where', 'why', 'how', '?']),
            lambda c: {'type': 'inquiry', 'needs_knowledge': True, 'act': 'answer'},
            weight=8
        )
        
        # Directive inference
        self.append_rule(
            'directive_detect',
            lambda c: any(w in c.get('q', '').lower() for w in ['show', 'display', 'compute', 'analyze']),
            lambda c: {'type': 'directive', 'needs_exec': True, 'act': 'execute'},
            weight=9
        )
        
        # Assistance inference
        self.append_rule(
            'assist_detect',
            lambda c: any(w in c.get('q', '').lower() for w in ['help', 'assist', 'support']),
            lambda c: {'type': 'assistance', 'provide_guide': True, 'act': 'help'},
            weight=10
        )
        
    def append_rule(self, rule_name, cond_fn, act_fn, weight=0):
        """Add new inference rule"""
        rule = InferenceRule(rule_name, cond_fn, act_fn, weight)
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.weight, reverse=True)
        
    def infer(self, query_txt, ctx_data=None):
        """
        Perform inference on query
        """
        
        inf_ctx = {
            'q': query_txt,
            'ts': dt.now().isoformat(),
            'ctx': ctx_data or {}
        }
        
        # Test all rules
        fired_rules = []
        rule_results = []
        
        for rule in self.rules:
            if rule.test_condition(inf_ctx):
                result = rule.apply_action(inf_ctx)
                fired_rules.append(rule.rule_name)
                rule_results.append(result)
                
        # Synthesize
        synth_result = self._synthesize_results(inf_ctx, fired_rules, rule_results)
        
        # Log
        self.inference_log.append({
            'query': query_txt,
            'fired': fired_rules,
            'ts': inf_ctx['ts'],
            'result': synth_result
        })
        
        return synth_result
    
    def _synthesize_results(self, ctx, fired, results):
        """Synthesize multiple results"""
        
        if not results:
            return {
                'type': 'default',
                'act': 'general',
                'fired': [],
                'certainty': 0.3
            }
            
        # Primary from highest weight
        primary = results[0] if results else {}
        
        # Combine
        synth = {
            'type': primary.get('type', 'default'),
            'act': primary.get('act', 'general'),
            'fired': fired,
            'certainty': min(0.95, 0.5 + (len(fired) * 0.15)),
            'aux_ctx': {}
        }
        
        # Aggregate auxiliary context
        for res in results:
            for k, v in res.items():
                if k not in ['type', 'act']:
                    synth['aux_ctx'][k] = v
                    
        return synth
    
    def rule_metrics(self):
        """Get rule statistics"""
        
        rule_map = {}
        for rule in self.rules:
            rule_map[rule.rule_name] = {
                'weight': rule.weight,
                'fires': rule.fire_cnt
            }
            
        return {
            'rule_cnt': len(self.rules),
            'inferences': len(self.inference_log),
            'rule_stats': rule_map
        }
