import { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import { Navbar } from './components/Navbar';
import { DashboardOverview } from './components/DashboardOverview';
import { CourseSpreadsheet } from './components/CourseSpreadsheet';
import { WhatIfSimulator } from './components/WhatIfSimulator';
import { TimelineTracker } from './components/TimelineTracker';
import { CourseData, calculateSemester, calculateCourse } from './utils/calculator';

// Import starter JSONs
import csn305Raw from './data/csn305.json';
import dat330Raw from './data/dat330.json';
import mst300Raw from './data/mst300.json';
import psy262Raw from './data/psy262.json';
import sec320Raw from './data/sec320.json';
import ops345Raw from './data/ops345.json';
import wtp100Raw from './data/wtp100.json';
import { LayoutDashboard, Sparkles, Calendar, BookOpen } from 'lucide-react';

const STARTER_COURSES: CourseData[] = [
  csn305Raw as CourseData,
  dat330Raw as CourseData,
  mst300Raw as CourseData,
  psy262Raw as CourseData,
  sec320Raw as CourseData,
  ops345Raw as CourseData,
  wtp100Raw as CourseData,
];

const STORAGE_KEY = 'seneca_grade_calc_data_v1';

export function App() {
  const [courses, setCourses] = useState<CourseData[]>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved courses', e);
      }
    }
    return STARTER_COURSES;
  });

  const [activeTab, setActiveTab] = useState<string>('OVERVIEW');

  // Save to LocalStorage on change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(courses));
  }, [courses]);

  const semesterCalc = calculateSemester(courses);

  const handleUpdateScore = (courseCode: string, itemId: string, earnedPoints: number | null) => {
    setCourses(prev =>
      prev.map(c => {
        if (c.course_code !== courseCode) return c;
        return {
          ...c,
          categories: c.categories.map(cat => ({
            ...cat,
            items: cat.items.map(it => {
              if (it.id !== itemId) return it;
              const newStatus = earnedPoints !== null ? 'Done' : it.status;
              return { ...it, earned_points: earnedPoints, status: newStatus };
            })
          }))
        };
      })
    );
  };

  const handleUpdateStatus = (courseCode: string, itemId: string, status: "Not Started" | "In Progress" | "Done") => {
    setCourses(prev =>
      prev.map(c => {
        if (c.course_code !== courseCode) return c;
        return {
          ...c,
          categories: c.categories.map(cat => ({
            ...cat,
            items: cat.items.map(it => {
              if (it.id !== itemId) return it;
              return { ...it, status };
            })
          }))
        };
      })
    );
  };

  const handleResetData = () => {
    if (confirm('Reset all marks to initial syllabus starter data?')) {
      setCourses(STARTER_COURSES);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  // Browser-side Excel export using SheetJS
  const handleExportExcel = () => {
    const wb = XLSX.utils.book_new();

    // 1. Dashboard Overview Sheet
    const dashRows: any[] = [
      ['Seneca Polytechnic - CTY Semester 3 Grade Summary'],
      ['Cumulative GPA', semesterCalc.cumulative_gpa, 'Projected GPA', semesterCalc.projected_gpa],
      ['Technical Avg', semesterCalc.technical_current_average ? `${semesterCalc.technical_current_average}%` : 'N/A', 'Overall Avg', semesterCalc.overall_current_average ? `${semesterCalc.overall_current_average}%` : 'N/A'],
      [],
      ['Code', 'Course Name', 'Credits', 'Type', 'Completed %', 'Current Avg %', 'Projected %', 'Grade', 'GPA', 'Hurdles']
    ];

    courses.forEach(c => {
      const calc = calculateCourse(c);
      dashRows.push([
        c.course_code,
        c.course_name,
        c.credits,
        c.is_technical ? 'Technical' : 'General',
        `${calc.completed_weight.toFixed(1)}%`,
        calc.current_average !== null ? `${calc.current_average.toFixed(1)}%` : 'N/A',
        `${calc.projected_final.toFixed(1)}%`,
        calc.letter_grade,
        calc.gpa_points !== null ? calc.gpa_points : 'N/A',
        calc.hurdle_passed ? 'PASSED' : calc.hurdle_warnings.join('; ')
      ]);
    });

    const wsDash = XLSX.utils.aoa_to_sheet(dashRows);
    XLSX.utils.book_append_sheet(wb, wsDash, 'Dashboard');

    // 2. Individual Course Sheets
    courses.forEach(c => {
      const calc = calculateCourse(c);
      const rows: any[] = [
        [`${c.course_code}: ${c.course_name}`],
        [`Credits: ${c.credits}`, `Current Avg: ${calc.current_average !== null ? calc.current_average.toFixed(1) + '%' : 'N/A'}`, `Projected: ${calc.projected_final.toFixed(1)}%`, `Grade: ${calc.letter_grade}`],
        [],
        ['Category', 'Assessment Item', 'Weight %', 'Max Points', 'Earned Points', 'Score %', 'Weighted %', 'Due Date', 'Status']
      ];

      c.categories.forEach(cat => {
        cat.items.forEach(it => {
          const score = it.earned_points !== null ? (it.earned_points / it.max_points) * 100 : null;
          const weighted = score !== null ? (score / 100) * it.weight_percent : null;
          rows.push([
            cat.name,
            it.name,
            `${it.weight_percent}%`,
            it.max_points,
            it.earned_points !== null ? it.earned_points : '',
            score !== null ? `${score.toFixed(1)}%` : '',
            weighted !== null ? `${weighted.toFixed(2)}%` : '',
            it.due_date || '',
            it.status
          ]);
        });
      });

      const wsCourse = XLSX.utils.aoa_to_sheet(rows);
      XLSX.utils.book_append_sheet(wb, wsCourse, c.course_code);
    });

    XLSX.writeFile(wb, 'seneca_semester_3_grade_calculator.xlsx');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col">
      <Navbar onExportExcel={handleExportExcel} onResetData={handleResetData} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-3 mb-6 border-b border-slate-200 dark:border-slate-800 scrollbar-none">
          <button
            onClick={() => setActiveTab('OVERVIEW')}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg transition whitespace-nowrap ${
              activeTab === 'OVERVIEW'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard & GPA</span>
          </button>

          {/* Individual Course Tabs */}
          {courses.map(c => {
            const calc = calculateCourse(c);
            const isSelected = activeTab === c.course_code;
            return (
              <button
                key={c.course_code}
                onClick={() => setActiveTab(c.course_code)}
                className={`flex items-center gap-2 px-3 py-2 text-xs font-bold rounded-lg transition whitespace-nowrap ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>{c.course_code}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-black ${
                  isSelected ? 'bg-blue-800 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                }`}>
                  {calc.letter_grade}
                </span>
              </button>
            );
          })}

          <button
            onClick={() => setActiveTab('WHAT_IF')}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg transition whitespace-nowrap ${
              activeTab === 'WHAT_IF'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>What-If Simulator</span>
          </button>

          <button
            onClick={() => setActiveTab('TIMELINE')}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg transition whitespace-nowrap ${
              activeTab === 'TIMELINE'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
            }`}
          >
            <Calendar className="w-4 h-4" />
            <span>Timeline</span>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'OVERVIEW' && (
          <DashboardOverview
            courses={courses}
            semesterCalc={semesterCalc}
            onSelectCourse={(code) => setActiveTab(code)}
          />
        )}

        {courses.some(c => c.course_code === activeTab) && (
          <CourseSpreadsheet
            course={courses.find(c => c.course_code === activeTab)!}
            onUpdateScore={handleUpdateScore}
            onUpdateStatus={handleUpdateStatus}
          />
        )}

        {activeTab === 'WHAT_IF' && (
          <WhatIfSimulator courses={courses} />
        )}

        {activeTab === 'TIMELINE' && (
          <TimelineTracker courses={courses} onUpdateStatus={handleUpdateStatus} />
        )}
      </main>

      <footer className="py-4 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500">
        Seneca Polytechnic Computer Systems Technology (CTY) Semester 3 • Extracted via ExtendLM MCP & Gemini Notebook
      </footer>
    </div>
  );
}

export default App;
