"""
Interactive Floating Interface
Custom Tkinter canvas with animated background
"""

import tkinter as gui
from tkinter import ttk, scrolledtext as stxt
import threading as thr
from datetime import datetime as dt
import random as rnd
import math


class ParticleField:
    """Animated particle background"""
    
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.w = w
        self.h = h
        self.dots = []
        self.active = True
        self.frame = 0
        
        self._spawn_dots()
        
    def _spawn_dots(self):
        """Create particle dots"""
        for _ in range(30):
            dot = {
                'px': rnd.randint(0, self.w),
                'py': rnd.randint(0, self.h),
                'dx': rnd.uniform(-1, 1),
                'dy': rnd.uniform(-1, 1),
                'r': rnd.randint(2, 5),
                'col': self._dot_color()
            }
            self.dots.append(dot)
            
    def _dot_color(self):
        """Generate dot color"""
        cols = ['#1a5490', '#2a6cb0', '#3a7cc0', '#4a8cd0']
        return rnd.choice(cols)
    
    def tick(self):
        """Animate one tick"""
        if not self.active:
            return
            
        self.canvas.delete('dot')
        
        for dot in self.dots:
            # Move
            dot['px'] += dot['dx']
            dot['py'] += dot['dy']
            
            # Bounce
            if dot['px'] <= 0 or dot['px'] >= self.w:
                dot['dx'] *= -1
            if dot['py'] <= 0 or dot['py'] >= self.h:
                dot['dy'] *= -1
                
            # Clamp
            dot['px'] = max(0, min(self.w, dot['px']))
            dot['py'] = max(0, min(self.h, dot['py']))
            
            # Draw
            self.canvas.create_oval(
                dot['px'] - dot['r'],
                dot['py'] - dot['r'],
                dot['px'] + dot['r'],
                dot['py'] + dot['r'],
                fill=dot['col'],
                outline='',
                tags='dot'
            )
            
        self.frame += 1
        
        # Draw links
        if self.frame % 3 == 0:
            self._draw_links()
            
    def _draw_links(self):
        """Draw connections between nearby dots"""
        for i, d1 in enumerate(self.dots):
            for d2 in self.dots[i+1:]:
                dist = math.sqrt((d1['px'] - d2['px'])**2 + (d1['py'] - d2['py'])**2)
                if dist < 100:
                    alpha = int((1 - dist/100) * 50)
                    col = f'#{alpha:02x}{alpha:02x}{alpha+50:02x}'
                    self.canvas.create_line(
                        d1['px'], d1['py'], d2['px'], d2['py'],
                        fill=col, width=1, tags='dot'
                    )
    
    def halt(self):
        """Stop animation"""
        self.active = False


class DynamicViewport:
    """Main interactive interface"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.window = None
        self.running = False
        self.cert_meter = None
        self.particles = None
        
    def setup(self):
        """Setup window and widgets"""
        
        self.window = gui.Tk()
        self.window.title("THALOS PRIME - SBI Interface")
        self.window.geometry("900x700")
        self.window.configure(bg='#0a0a0a')
        self.window.attributes('-alpha', 0.95)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self._build_widgets()
        self.running = True
        
    def _build_widgets(self):
        """Build all UI widgets"""
        
        # Particle canvas
        self.bg_canvas = gui.Canvas(
            self.window, width=900, height=200,
            bg='#0a0a0a', highlightthickness=0
        )
        self.bg_canvas.pack(fill=gui.BOTH, expand=False)
        
        self.particles = ParticleField(self.bg_canvas, 900, 200)
        
        # Title
        title = gui.Label(
            self.window, text="⚡ THALOS PRIME SBI ⚡",
            font=('Courier', 18, 'bold'),
            bg='#0a0a0a', fg='#00ff88'
        )
        title.pack(pady=10)
        
        # Status
        status_box = gui.Frame(self.window, bg='#0a0a0a')
        status_box.pack(pady=5)
        
        self.status_txt = gui.Label(
            status_box, text="Status: Ready",
            font=('Courier', 10), bg='#0a0a0a', fg='#00ff88'
        )
        self.status_txt.pack(side=gui.LEFT, padx=10)
        
        # Certainty meter
        cert_box = gui.Frame(self.window, bg='#0a0a0a')
        cert_box.pack(pady=5)
        
        gui.Label(
            cert_box, text="Certainty:",
            font=('Courier', 10), bg='#0a0a0a', fg='#00ff88'
        ).pack(side=gui.LEFT)
        
        self.cert_var = gui.DoubleVar(value=0.0)
        self.cert_meter = ttk.Progressbar(
            cert_box, variable=self.cert_var,
            maximum=100, length=200, mode='determinate'
        )
        self.cert_meter.pack(side=gui.LEFT, padx=10)
        
        self.cert_lbl = gui.Label(
            cert_box, text="0%",
            font=('Courier', 10), bg='#0a0a0a', fg='#00ff88'
        )
        self.cert_lbl.pack(side=gui.LEFT)
        
        # Input
        inp_box = gui.Frame(self.window, bg='#0a0a0a')
        inp_box.pack(pady=10, padx=20, fill=gui.X)
        
        gui.Label(
            inp_box, text="Query:",
            font=('Courier', 11, 'bold'), bg='#0a0a0a', fg='#00ff88'
        ).pack(anchor=gui.W)
        
        self.input_box = gui.Text(
            inp_box, height=3, font=('Courier', 10),
            bg='#1a1a1a', fg='#00ff88', insertbackground='#00ff88',
            relief=gui.FLAT, borderwidth=2
        )
        self.input_box.pack(fill=gui.X, pady=5)
        
        # Buttons
        btn_box = gui.Frame(self.window, bg='#0a0a0a')
        btn_box.pack(pady=5)
        
        self.submit_btn = gui.Button(
            btn_box, text="🚀 Process",
            font=('Courier', 11, 'bold'),
            bg='#1a5a3a', fg='#ffffff',
            activebackground='#2a7a5a',
            command=self._on_submit,
            relief=gui.FLAT, padx=20, pady=5
        )
        self.submit_btn.pack(side=gui.LEFT, padx=5)
        
        self.clear_btn = gui.Button(
            btn_box, text="Clear",
            font=('Courier', 11),
            bg='#5a1a1a', fg='#ffffff',
            activebackground='#7a2a2a',
            command=self._on_clear,
            relief=gui.FLAT, padx=20, pady=5
        )
        self.clear_btn.pack(side=gui.LEFT, padx=5)
        
        # Output
        out_box = gui.Frame(self.window, bg='#0a0a0a')
        out_box.pack(pady=10, padx=20, fill=gui.BOTH, expand=True)
        
        gui.Label(
            out_box, text="Response:",
            font=('Courier', 11, 'bold'), bg='#0a0a0a', fg='#00ff88'
        ).pack(anchor=gui.W)
        
        self.output_box = stxt.ScrolledText(
            out_box, font=('Courier', 10),
            bg='#1a1a1a', fg='#00ff88',
            relief=gui.FLAT, borderwidth=2,
            state=gui.DISABLED
        )
        self.output_box.pack(fill=gui.BOTH, expand=True, pady=5)
        
        # Bind keys
        self.input_box.bind('<Control-Return>', lambda e: self._on_submit())
        
    def _on_submit(self):
        """Handle submit"""
        
        q_txt = self.input_box.get('1.0', gui.END).strip()
        
        if not q_txt:
            return
            
        self.status_txt.config(text="Status: Processing...", fg='#ffaa00')
        self.submit_btn.config(state=gui.DISABLED)
        
        # Process in thread
        t = thr.Thread(target=self._process_async, args=(q_txt,))
        t.daemon = True
        t.start()
        
    def _process_async(self, q_txt):
        """Process in background"""
        
        if self.callback:
            resp = self.callback(q_txt)
            self.window.after(0, self._show_response, resp)
        else:
            # Default
            resp = {
                'answer': f"Processed: {q_txt}",
                'certainty': 0.75,
                'timestamp': dt.now().isoformat()
            }
            self.window.after(0, self._show_response, resp)
            
    def _show_response(self, resp):
        """Display response"""
        
        self.output_box.config(state=gui.NORMAL)
        self.output_box.delete('1.0', gui.END)
        
        # Format
        out_txt = f"[{resp.get('timestamp', 'N/A')}]\n\n"
        out_txt += resp.get('answer', 'No response')
        out_txt += f"\n\n--- Metrics ---\n"
        out_txt += f"Certainty: {resp.get('certainty', 0.0):.2%}\n"
        
        if 'params_used' in resp:
            out_txt += f"Parameters: {resp['params_used']:,}\n"
        if 'wave_depth' in resp:
            out_txt += f"Wave Depth: {resp['wave_depth']} layers\n"
            
        self.output_box.insert('1.0', out_txt)
        self.output_box.config(state=gui.DISABLED)
        
        # Update meter
        cert_pct = resp.get('certainty', 0.0) * 100
        self.cert_var.set(cert_pct)
        self.cert_lbl.config(text=f"{cert_pct:.1f}%")
        
        # Update status
        self.status_txt.config(text="Status: Ready", fg='#00ff88')
        self.submit_btn.config(state=gui.NORMAL)
        
    def _on_clear(self):
        """Clear displays"""
        self.output_box.config(state=gui.NORMAL)
        self.output_box.delete('1.0', gui.END)
        self.output_box.config(state=gui.DISABLED)
        
        self.input_box.delete('1.0', gui.END)
        self.cert_var.set(0)
        self.cert_lbl.config(text="0%")
        
    def _animate_loop(self):
        """Animation loop"""
        if self.running and self.particles:
            self.particles.tick()
            self.window.after(50, self._animate_loop)
            
    def start(self):
        """Start the interface"""
        self.setup()
        self._animate_loop()
        self.window.mainloop()
        
    def stop(self):
        """Stop the interface"""
        self.running = False
        if self.particles:
            self.particles.halt()
        if self.window:
            self.window.quit()
