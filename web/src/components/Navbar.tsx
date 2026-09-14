import React from 'react';
import { Download, RotateCcw, GraduationCap, Github } from 'lucide-react';

interface NavbarProps {
  onExportExcel: () => void;
  onResetData: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onExportExcel, onResetData }) => {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center shadow-inner">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              Seneca CTY Grade Calculator
              <span className="text-xs bg-blue-500/20 text-blue-300 font-medium px-2 py-0.5 rounded-full border border-blue-400/30">
                ExtendLM MCP Ingested
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Computer Systems Technology • Fall 2026 • Seneca 4.0 Scale
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          <button
            onClick={onResetData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 hover:text-white rounded-md border border-slate-700 transition"
            title="Reset marks to default syllabus starter data"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          <button
            onClick={onExportExcel}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-emerald-600 hover:bg-emerald-500 rounded-md shadow transition"
            title="Download multi-tab Excel spreadsheet (.xlsx)"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Excel</span>
          </button>

          <a
            href="https://github.com/StickwoodJr/grade-calculator-mcp"
            target="_blank"
            rel="noreferrer"
            className="p-1.5 text-slate-400 hover:text-white transition"
            title="GitHub Repository"
          >
            <Github className="w-5 h-5" />
          </a>
        </div>
      </div>
    </header>
  );
};
