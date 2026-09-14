import React, { useState } from 'react';
import { CourseData } from '../utils/calculator';
import { Calendar, Filter, CheckCircle2, Clock, Circle } from 'lucide-react';

interface TimelineTrackerProps {
  courses: CourseData[];
  onUpdateStatus: (courseCode: string, itemId: string, status: "Not Started" | "In Progress" | "Done") => void;
}

export const TimelineTracker: React.FC<TimelineTrackerProps> = ({ courses, onUpdateStatus }) => {
  const [courseFilter, setCourseFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Flatten all items
  const allItems: {
    courseCode: string;
    itemId: string;
    name: string;
    category: string;
    weight: number;
    dueDate: string;
    status: "Not Started" | "In Progress" | "Done";
    earned: number | null;
    maxPoints: number;
  }[] = [];

  courses.forEach(c => {
    c.categories.forEach(cat => {
      cat.items.forEach(item => {
        allItems.push({
          courseCode: c.course_code,
          itemId: item.id,
          name: item.name,
          category: cat.name,
          weight: item.weight_percent,
          dueDate: item.due_date || 'TBA',
          status: item.status,
          earned: item.earned_points,
          maxPoints: item.max_points
        });
      });
    });
  });

  // Sort by date
  allItems.sort((a, b) => {
    if (a.dueDate === 'TBA') return 1;
    if (b.dueDate === 'TBA') return -1;
    return a.dueDate.localeCompare(b.dueDate);
  });

  // Filter items
  const filtered = allItems.filter(it => {
    if (courseFilter !== 'ALL' && it.courseCode !== courseFilter) return false;
    if (statusFilter !== 'ALL' && it.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Semester 3 Deliverables Timeline
            </h2>
            <p className="text-xs text-slate-500">
              Chronological schedule of all assignments, labs, quizzes, and tests across all courses
            </p>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Filter className="w-3.5 h-3.5" />
              <span>Filters:</span>
            </div>

            <select
              value={courseFilter}
              onChange={(e) => setCourseFilter(e.target.value)}
              className="text-xs px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300"
            >
              <option value="ALL">All Courses</option>
              {courses.map(c => (
                <option key={c.course_code} value={c.course_code}>{c.course_code}</option>
              ))}
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300"
            >
              <option value="ALL">All Statuses</option>
              <option value="Done">Done</option>
              <option value="In Progress">In Progress</option>
              <option value="Not Started">Not Started</option>
            </select>
          </div>
        </div>

        {/* Timeline Table */}
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700 text-sm">
            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-600 dark:text-slate-300 text-xs font-semibold">
              <tr>
                <th className="px-4 py-3 text-left w-12">Done</th>
                <th className="px-3 py-3 text-left">Course</th>
                <th className="px-4 py-3 text-left">Assessment Item</th>
                <th className="px-3 py-3 text-left">Category</th>
                <th className="px-3 py-3 text-right">Weight %</th>
                <th className="px-3 py-3 text-center">Due Date</th>
                <th className="px-4 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50">
              {filtered.map((it, idx) => {
                const isDone = it.status === 'Done';
                return (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition">
                    <td className="px-4 py-2.5 text-center">
                      <button
                        onClick={() => onUpdateStatus(it.courseCode, it.itemId, isDone ? 'Not Started' : 'Done')}
                        className={`p-1 rounded transition ${
                          isDone ? 'text-emerald-600' : 'text-slate-300 hover:text-slate-400'
                        }`}
                      >
                        {isDone ? (
                          <CheckCircle2 className="w-4 h-4 fill-emerald-100 dark:fill-emerald-950" />
                        ) : (
                          <Circle className="w-4 h-4" />
                        )}
                      </button>
                    </td>
                    <td className="px-3 py-2.5 font-bold text-blue-600 dark:text-blue-400">
                      {it.courseCode}
                    </td>
                    <td className={`px-4 py-2.5 font-medium ${isDone ? 'line-through text-slate-400' : 'text-slate-900 dark:text-white'}`}>
                      {it.name}
                    </td>
                    <td className="px-3 py-2.5 text-xs text-slate-500">
                      {it.category}
                    </td>
                    <td className="px-3 py-2.5 text-right font-mono text-slate-600 dark:text-slate-300">
                      {it.weight.toFixed(1)}%
                    </td>
                    <td className="px-3 py-2.5 text-center font-mono text-xs text-slate-600 dark:text-slate-400">
                      {it.dueDate}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                        it.status === 'Done'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                          : it.status === 'In Progress'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                          : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                      }`}>
                        {it.status === 'Done' ? <CheckCircle2 className="w-3 h-3" /> : it.status === 'In Progress' ? <Clock className="w-3 h-3" /> : null}
                        {it.status}
                      </span>
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
