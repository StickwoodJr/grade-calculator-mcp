import React from 'react';
import {
  CourseData,
  SemesterCalculation,
  calculateCourse
} from '../utils/calculator';
import { Award, AlertTriangle, CheckCircle2, TrendingUp, Code2, BookOpen, Layers } from 'lucide-react';

interface DashboardOverviewProps {
  courses: CourseData[];
  semesterCalc: SemesterCalculation;
  onSelectCourse: (courseCode: string) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  courses,
  semesterCalc,
  onSelectCourse
}) => {
  // Aggregate all hurdle warnings
  const allWarnings: { courseCode: string; message: string }[] = [];
  courses.forEach(c => {
    const calc = calculateCourse(c);
    calc.hurdle_warnings.forEach(w => {
      allWarnings.push({ courseCode: c.course_code, message: w });
    });
  });

  return (
    <div className="space-y-6">
      {/* Hurdle Alert Banner */}
      {allWarnings.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg shadow-sm">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-red-800">
                Passing Hurdle Attention Required ({allWarnings.length})
              </h3>
              <ul className="mt-1 text-xs text-red-700 list-disc list-inside space-y-1">
                {allWarnings.map((w, idx) => (
                  <li key={idx}>
                    <span className="font-bold">{w.courseCode}:</span> {w.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* Cumulative GPA */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Cumulative GPA
            </span>
            <Award className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {semesterCalc.cumulative_gpa.toFixed(2)}
            </span>
            <span className="text-xs font-medium text-slate-400">/ 4.0</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Official Seneca Scale</p>
        </div>

        {/* Projected GPA */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Projected GPA
            </span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {semesterCalc.projected_gpa.toFixed(2)}
            </span>
            <span className="text-xs font-medium text-slate-400">/ 4.0</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Based on remaining pace</p>
        </div>

        {/* Technical Major Average */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
              Technical Average
            </span>
            <Code2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="mt-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {semesterCalc.technical_current_average !== null ? `${semesterCalc.technical_current_average.toFixed(1)}%` : '—'}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">5 Tech Core Courses</p>
        </div>

        {/* Overall Graded Average */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Overall Average
            </span>
            <BookOpen className="w-4 h-4 text-slate-600" />
          </div>
          <div className="mt-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {semesterCalc.overall_current_average !== null ? `${semesterCalc.overall_current_average.toFixed(1)}%` : '—'}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">All Graded Courses</p>
        </div>

        {/* Semester Progress */}
        <div className="col-span-2 md:col-span-1 bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Deliverables
            </span>
            <Layers className="w-4 h-4 text-slate-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {semesterCalc.completed_items_count}
            </span>
            <span className="text-xs font-medium text-slate-400">/ {semesterCalc.total_items_count}</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${(semesterCalc.completed_items_count / Math.max(1, semesterCalc.total_items_count)) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Master Course Summary Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Semester 3 Course Summary
            </h2>
            <p className="text-xs text-slate-500">
              Click any course to view and edit individual assessment scores
            </p>
          </div>
          <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full font-medium">
            19.0 Total Credits
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700 text-sm">
            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-600 dark:text-slate-300 font-semibold text-xs">
              <tr>
                <th className="px-4 py-3 text-left">Code</th>
                <th className="px-4 py-3 text-left">Course Name</th>
                <th className="px-3 py-3 text-center">Credits</th>
                <th className="px-3 py-3 text-left">Type</th>
                <th className="px-3 py-3 text-right">Completed %</th>
                <th className="px-3 py-3 text-right">Current Avg</th>
                <th className="px-3 py-3 text-right">Projected</th>
                <th className="px-3 py-3 text-center">Grade</th>
                <th className="px-3 py-3 text-center">GPA</th>
                <th className="px-4 py-3 text-center">Hurdle Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50">
              {courses.map(course => {
                const calc = calculateCourse(course);
                const isTech = course.is_technical;
                const isSatUn = course.grading_type === "sat_un";

                return (
                  <tr
                    key={course.course_code}
                    onClick={() => onSelectCourse(course.course_code)}
                    className="hover:bg-blue-50/50 dark:hover:bg-slate-700/50 cursor-pointer transition"
                  >
                    <td className="px-4 py-3 font-bold text-blue-600 dark:text-blue-400">
                      {course.course_code}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">
                      {course.course_name}
                    </td>
                    <td className="px-3 py-3 text-center text-slate-500">
                      {course.credits.toFixed(1)}
                    </td>
                    <td className="px-3 py-3">
                      <span className={`inline-block px-2 py-0.5 text-xs rounded-md font-medium ${
                        isTech
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                          : isSatUn
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300'
                          : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                      }`}>
                        {isTech ? 'Technical Core' : isSatUn ? 'Co-op Prep' : 'General Ed'}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right font-mono text-slate-600 dark:text-slate-300">
                      {calc.completed_weight.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 text-right font-mono font-bold text-slate-900 dark:text-white">
                      {calc.current_average !== null ? `${calc.current_average.toFixed(1)}%` : '—'}
                    </td>
                    <td className="px-3 py-3 text-right font-mono font-bold text-slate-900 dark:text-white">
                      {calc.projected_final.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span className={`inline-block px-2 py-0.5 text-xs font-bold rounded ${
                        calc.letter_grade.startsWith('A')
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                          : calc.letter_grade.startsWith('B')
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                          : calc.letter_grade.startsWith('C')
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                          : calc.letter_grade === 'SAT'
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                      }`}>
                        {calc.letter_grade}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-center font-mono font-bold text-slate-700 dark:text-slate-300">
                      {calc.gpa_points !== null ? calc.gpa_points.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {calc.hurdle_passed ? (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium">
                          <CheckCircle2 className="w-4 h-4" /> Passed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-red-600 font-bold" title={calc.hurdle_warnings.join(', ')}>
                          <AlertTriangle className="w-4 h-4" /> Attention
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
