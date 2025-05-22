from PyQt5 import QtWidgets, QtGui, QtCore
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import csv
import os
import time
from datetime import datetime
import math

class GraphWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, graph_id=0):
        super().__init__(parent)
        self.parent = parent
        self.graph_id = graph_id
        self.is_recording = False
        self.start_time = 0
        self.last_update_time = 0
        self.update_interval = 0.025  # Bước nhảy 0.2s
        self.selected_variables = []
        self.record_data = {}
        
        # Main layout for graph widget
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin
        self.setLayout(self.layout)
        
        # Add header with graph ID and close button
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        graph_title = QtWidgets.QLabel(f"Graph {self.graph_id}")
        graph_title.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(graph_title)
        
        header_layout.addStretch()
        
        close_button = QtWidgets.QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setToolTip("Remove graph")
        close_button.clicked.connect(self.remove_graph)
        header_layout.addWidget(close_button)
        
        self.layout.addLayout(header_layout)
        
        # Create matplotlib figure - TĂNG CHIỀU CAO Ở ĐÂY
        self.figure = Figure(figsize=(8, 8), dpi=100)  # Tăng chiều cao từ 3 lên 6
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)  # Tăng chiều cao tối thiểu từ 200 lên 400
        self.canvas.setMaximumHeight(600)  # Tăng chiều cao tối đa từ 200 lên 500
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(f'Graph {self.graph_id}')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.grid(True)
        
        # Add to layout
        self.layout.addWidget(self.canvas)
        
        # Controls for graph - giảm kích thước và không gian
        self.control_layout = QtWidgets.QHBoxLayout()
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(2)
        
        # Variable selection for graph with multi-selection
        self.variable_selector = QtWidgets.QComboBox()
        self.variable_selector.setFixedHeight(20)
        self.variable_selector.setPlaceholderText("Select variable")
        self.control_layout.addWidget(self.variable_selector)
        
        # Add button
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.setFixedHeight(20)
        self.add_button.clicked.connect(self.add_variable)
        self.control_layout.addWidget(self.add_button)
        
        # Recording controls
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.setFixedHeight(20)
        self.start_button.clicked.connect(self.start_recording)
        self.control_layout.addWidget(self.start_button)
        
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.setFixedHeight(20)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.control_layout.addWidget(self.stop_button)
        
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.reset_button.setFixedHeight(20)
        self.reset_button.clicked.connect(self.reset_graph)
        self.control_layout.addWidget(self.reset_button)
        
        self.export_button = QtWidgets.QPushButton("CSV")
        self.export_button.setFixedHeight(20)
        self.export_button.clicked.connect(self.export_data)
        self.control_layout.addWidget(self.export_button)
        
        self.layout.addLayout(self.control_layout)
        
        # Selected variables display
        self.selected_layout = QtWidgets.QHBoxLayout()
        self.selected_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_layout.setSpacing(2)
        
        self.selected_label = QtWidgets.QLabel("Selected:")
        self.selected_label.setFixedWidth(50)
        self.selected_layout.addWidget(self.selected_label)
        
        self.selected_list = QtWidgets.QLabel("None")
        self.selected_layout.addWidget(self.selected_list)
        
        self.remove_button = QtWidgets.QPushButton("×")
        self.remove_button.setFixedSize(20, 20)
        self.remove_button.clicked.connect(self.remove_variable)
        self.selected_layout.addWidget(self.remove_button)
        
        self.layout.addLayout(self.selected_layout)
        
        # Thêm đường phân cách
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

    def remove_graph(self):
        """Remove this graph from parent visualization"""
        if self.parent and hasattr(self.parent, "graphs"):
            # Remove from parent's graph list
            if self in self.parent.graphs:
                self.parent.graphs.remove(self)
            
            # Remove widget from layout
            self.setParent(None)
            self.deleteLater()
    
    def update_variable_selector(self, variables):
        """Update the variable selector with new variables"""
        current_items = [self.variable_selector.itemText(i) for i in range(self.variable_selector.count())]
        for var in variables:
            if var not in current_items:
                self.variable_selector.addItem(var)
    
    def add_variable(self):
        """Add selected variable to the graph"""
        variable = self.variable_selector.currentText()
        if variable and variable not in self.selected_variables:
            self.selected_variables.append(variable)
            self.update_selected_list()
            # Create entry in record data
            if variable not in self.record_data:
                self.record_data[variable] = {'time': [], 'value': []}
    
    def remove_variable(self):
        """Remove variable from graph"""
        # Show dialog to select variable to remove
        if not self.selected_variables:
            return
            
        item, ok = QtWidgets.QInputDialog.getItem(
            self, "Remove Variable", "Select variable to remove:",
            self.selected_variables, 0, False)
        
        if ok and item:
            self.selected_variables.remove(item)
            if item in self.record_data:
                del self.record_data[item]
            self.update_selected_list()
            self.update_graph()
    
    def update_selected_list(self):
        """Update the display of selected variables"""
        if self.selected_variables:
            self.selected_list.setText(", ".join(self.selected_variables))
        else:
            self.selected_list.setText("None")
    
    def start_recording(self):
        """Start recording data"""
        if not self.selected_variables:
            QtWidgets.QMessageBox.warning(self, "No Variables", "Please add variables to record first.")
            return
            
        self.is_recording = True
        self.start_time = time.time()
        self.last_update_time = 0  # Reset thời điểm cập nhật cuối
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Reset dữ liệu ghi
        for var in self.selected_variables:
            self.record_data[var] = {'time': [], 'value': []}
            
        # Reset biểu đồ
        self.ax.clear()
        self.ax.set_title(f'Graph {self.graph_id} - Recording')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.grid(True)
        self.canvas.draw()

    def stop_recording(self):
        """Stop recording data and rescale the graph to show all data from 0.0s"""
        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Kiểm tra xem có dữ liệu để hiển thị không
        has_data = False
        for var in self.selected_variables:
            if var in self.record_data and self.record_data[var]['time']:
                has_data = True
                break
                
        if has_data:
            # Cập nhật biểu đồ để hiển thị tất cả dữ liệu đã ghi
            self.ax.clear()
            
            # Vẽ dữ liệu của mỗi biến
            for var in self.selected_variables:
                if var in self.record_data and self.record_data[var]['time']:
                    self.ax.plot(
                        self.record_data[var]['time'],
                        self.record_data[var]['value'],
                        label=var
                    )
                    
            # Đặt phạm vi trục X từ 0 đến thời gian tối đa đã ghi
            max_time = 0
            for var in self.selected_variables:
                if var in self.record_data and self.record_data[var]['time']:
                    if self.record_data[var]['time']:
                        max_time = max(max_time, max(self.record_data[var]['time']))
            
            # Làm tròn max_time lên 1.0s gần nhất để biểu đồ đẹp hơn
            max_time = math.ceil(max_time)
            self.ax.set_xlim(0, max_time)
            
            # Tạo các điểm đánh dấu trục x với bước 0.2s
            x_ticks = np.arange(0, max_time + self.update_interval, self.update_interval)
            self.ax.set_xticks(x_ticks)
            
            # Chỉ hiển thị nhãn cho các giây chẵn để tránh quá nhiều nhãn
            x_tick_labels = [f"{x:.1f}" if x % 1.0 == 0 else "" for x in x_ticks]
            self.ax.set_xticklabels(x_tick_labels)
            
            # Cập nhật tiêu đề và nhãn
            self.ax.set_title(f'Graph {self.graph_id} - Stopped')
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Value')
            self.ax.grid(True)
            self.ax.legend()
            
            # Buộc vẽ lại với tỷ lệ đã cập nhật
            self.canvas.draw()
            
            print(f"Graph {self.graph_id} stopped and rescaled to show full data from 0.0s to {max_time}s")
        else:
            self.ax.set_title(f'Graph {self.graph_id} - Stopped (No Data)')
            self.canvas.draw()
    
    def reset_graph(self):
        """Reset the graph"""
        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Reset record data
        for var in self.selected_variables:
            self.record_data[var] = {'time': [], 'value': []}
            
        # Reset graph
        self.ax.clear()
        self.ax.set_title(f'Graph {self.graph_id}')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.grid(True)
        self.canvas.draw()
    
    def export_data(self):
        """Export recorded data to CSV"""
        if not any(self.record_data.values()):
            QtWidgets.QMessageBox.warning(self, "No Data", "No data to export.")
            return
            
        # Open file dialog to choose save location
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Create header row with time and all variables
                    header = ['Time (s)']
                    for var in self.selected_variables:
                        if var in self.record_data and self.record_data[var]['time']:
                            header.append(var)
                    
                    writer.writerow(header)
                    
                    # Find the max number of data points
                    max_points = 0
                    for var in self.selected_variables:
                        if var in self.record_data:
                            max_points = max(max_points, len(self.record_data[var]['time']))
                    
                    # Write data rows
                    for i in range(max_points):
                        row = []
                        
                        # Add time
                        for var in self.selected_variables:
                            if var in self.record_data and i < len(self.record_data[var]['time']):
                                row.append(self.record_data[var]['time'][i])
                                break
                        else:
                            row.append('')
                        
                        # Add values for each variable
                        for var in self.selected_variables:
                            if var in self.record_data and i < len(self.record_data[var]['value']):
                                row.append(self.record_data[var]['value'][i])
                            else:
                                row.append('')
                        
                        writer.writerow(row)
                
                QtWidgets.QMessageBox.information(self, "Export Successful", "Data exported successfully!")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Export Error", f"Error exporting data: {str(e)}")
    
    def update_data(self, variable, value):
        """Update data for a variable if it's selected for this graph"""
        if variable not in self.selected_variables:
            return
        
        current_time = time.time()
        
        # Tính thời điểm hiển thị
        if self.is_recording:
            # Tính thời gian tương đối từ khi bắt đầu ghi
            elapsed_time = current_time - self.start_time
            
            # Xác định thời điểm hiển thị kế tiếp dựa trên bước nhảy
            display_time = self.last_update_time + self.update_interval
            
            # Nếu chưa đến thời điểm cập nhật kế tiếp, bỏ qua
            if elapsed_time < display_time:
                return
                
            # Cập nhật thời điểm cuối cùng được hiển thị
            self.last_update_time = int(elapsed_time / self.update_interval) * self.update_interval
            
            # Cập nhật dữ liệu
            if variable not in self.record_data:
                self.record_data[variable] = {'time': [], 'value': []}
                
            self.record_data[variable]['time'].append(self.last_update_time)
            self.record_data[variable]['value'].append(value)
        else:
            # Trong chế độ xem (không ghi), hiển thị dữ liệu với bước nhảy đều
            if variable not in self.record_data:
                self.record_data[variable] = {'time': [], 'value': []}
            
            # Thêm dữ liệu mới
            if not self.record_data[variable]['time']:
                next_time = 0
            else:
                next_time = self.record_data[variable]['time'][-1] + self.update_interval
                
            self.record_data[variable]['time'].append(next_time)
            self.record_data[variable]['value'].append(value)
            
            # Giới hạn số lượng điểm hiển thị khi không ghi
            max_points = 50  # Giữ 50 điểm dữ liệu gần nhất
            if len(self.record_data[variable]['time']) > max_points:
                self.record_data[variable]['time'].pop(0)
                self.record_data[variable]['value'].pop(0)
        
        # Cập nhật biểu đồ
        self.update_graph()
    
    def update_graph(self):
        """Update the graph with new data"""
        if not self.selected_variables:
            return
            
        self.ax.clear()
        
        # Plot each variable
        for var in self.selected_variables:
            if var in self.record_data and self.record_data[var]['time']:
                self.ax.plot(
                    self.record_data[var]['time'], 
                    self.record_data[var]['value'], 
                    label=var
                )
        
        # Update labels and legend
        self.ax.set_title(f'Graph {self.graph_id}' + (' - Recording' if self.is_recording else ''))
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.grid(True)
        self.ax.legend()
        
        # Redraw
        self.canvas.draw()