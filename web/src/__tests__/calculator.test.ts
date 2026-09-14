import { describe, it, expect } from 'vitest';
import {
  getSenecaLetterGrade,
  getSenecaGpaPoints,
  calculateCourse,
  calculateSemester,
  calculateWhatIf,
  CourseData
} from '../utils/calculator';

describe('Seneca GPA and Letter Grade Conversions', () => {
  it('correctly maps percentages to Seneca letter grades', () => {
    expect(getSenecaLetterGrade(95)).toBe('A+');
    expect(getSenecaLetterGrade(85)).toBe('A');
    expect(getSenecaLetterGrade(77)).toBe('B+');
    expect(getSenecaLetterGrade(72)).toBe('B');
    expect(getSenecaLetterGrade(67)).toBe('C+');
    expect(getSenecaLetterGrade(61)).toBe('C');
    expect(getSenecaLetterGrade(56)).toBe('D+');
    expect(getSenecaLetterGrade(51)).toBe('D');
    expect(getSenecaLetterGrade(45)).toBe('F');
  });

  it('handles SAT/UN pass-fail grading', () => {
    expect(getSenecaLetterGrade(85, true)).toBe('SAT');
    expect(getSenecaLetterGrade(79, true)).toBe('UN');
  });

  it('maps letter grades to 4.0 GPA scale points', () => {
    expect(getSenecaGpaPoints('A+')).toBe(4.0);
    expect(getSenecaGpaPoints('A')).toBe(4.0);
    expect(getSenecaGpaPoints('B+')).toBe(3.5);
    expect(getSenecaGpaPoints('B')).toBe(3.0);
    expect(getSenecaGpaPoints('C+')).toBe(2.5);
    expect(getSenecaGpaPoints('C')).toBe(2.0);
    expect(getSenecaGpaPoints('D+')).toBe(1.5);
    expect(getSenecaGpaPoints('D')).toBe(1.0);
    expect(getSenecaGpaPoints('F')).toBe(0.0);
    expect(getSenecaGpaPoints('SAT')).toBeNull();
  });
});

describe('Course Calculation & Hurdle Monitoring', () => {
  const sampleCourse: CourseData = {
    course_code: 'CSN305',
    course_name: 'Virtualization & Cloud',
    credits: 3.0,
    term: 'Fall 2026',
    is_technical: true,
    grading_type: 'percentage_gpa',
    grade_scale: 'Seneca 4.0',
    categories: [
      {
        category_id: 'labs',
        name: 'Labs',
        weight_percent: 40.0,
        items: [
          { id: 'l1', name: 'Lab 1', weight_percent: 20.0, max_points: 100, earned_points: 90, due_date: null, status: 'Done' },
          { id: 'l2', name: 'Lab 2', weight_percent: 20.0, max_points: 100, earned_points: null, due_date: null, status: 'Not Started' }
        ]
      },
      {
        category_id: 'tests',
        name: 'Tests',
        weight_percent: 60.0,
        items: [
          { id: 't1', name: 'Test 1', weight_percent: 30.0, max_points: 100, earned_points: 40, due_date: null, status: 'Done' },
          { id: 't2', name: 'Test 2', weight_percent: 30.0, max_points: 100, earned_points: null, due_date: null, status: 'Not Started' }
        ]
      }
    ],
    hurdles: [
      {
        type: 'category_average',
        target_category: 'tests',
        min_percentage: 50.0,
        description: 'Achieve >= 50% on all tests'
      }
    ]
  };

  it('calculates completed and earned weight accurately', () => {
    const calc = calculateCourse(sampleCourse);
    // Lab 1 (20% wt, earned 90% = 18%) + Test 1 (30% wt, earned 40% = 12%)
    expect(calc.completed_weight).toBe(50.0);
    expect(calc.earned_weight).toBe(30.0);
    expect(calc.current_average).toBe(60.0); // 30/50 * 100
  });

  it('triggers hurdle alert when test average is below 50%', () => {
    const calc = calculateCourse(sampleCourse);
    // Test 1 is 40% which is < 50% hurdle threshold
    expect(calc.hurdle_passed).toBe(false);
    expect(calc.hurdle_warnings.length).toBeGreaterThan(0);
    expect(calc.hurdle_warnings[0]).toContain('Hurdle Alert');
  });

  it('resolves hurdle when test average improves above 50%', () => {
    const improvedCourse: CourseData = JSON.parse(JSON.stringify(sampleCourse));
    improvedCourse.categories[1].items[0].earned_points = 80; // 80% on Test 1
    const calc = calculateCourse(improvedCourse);
    expect(calc.hurdle_passed).toBe(true);
    expect(calc.hurdle_warnings.length).toBe(0);
  });
});

describe('Semester Overview & Technical Average Isolation', () => {
  const techCourse: CourseData = {
    course_code: 'SEC320',
    course_name: 'Forensics',
    credits: 3.0,
    term: 'Fall 2026',
    is_technical: true,
    grading_type: 'percentage_gpa',
    grade_scale: 'Seneca 4.0',
    categories: [{
      category_id: 'labs',
      name: 'Labs',
      weight_percent: 100.0,
      items: [{ id: '1', name: 'Lab', weight_percent: 100.0, max_points: 100, earned_points: 90, due_date: null, status: 'Done' }]
    }]
  };

  const genEdCourse: CourseData = {
    course_code: 'PSY262',
    course_name: 'Mindfulness',
    credits: 3.0,
    term: 'Fall 2026',
    is_technical: false,
    grading_type: 'percentage_gpa',
    grade_scale: 'Seneca 4.0',
    categories: [{
      category_id: 'assign',
      name: 'Assignments',
      weight_percent: 100.0,
      items: [{ id: '1', name: 'Asgn', weight_percent: 100.0, max_points: 100, earned_points: 70, due_date: null, status: 'Done' }]
    }]
  };

  const satCourse: CourseData = {
    course_code: 'WTP100',
    course_name: 'Co-op Prep',
    credits: 1.0,
    term: 'Fall 2026',
    is_technical: false,
    grading_type: 'sat_un',
    grade_scale: 'SAT/UN',
    categories: [{
      category_id: 'mods',
      name: 'Modules',
      weight_percent: 100.0,
      items: [{ id: '1', name: 'Mod 1', weight_percent: 100.0, max_points: 100, earned_points: 100, due_date: null, status: 'Done' }]
    }]
  };

  it('isolates technical course averages from general electives and excludes SAT/UN from GPA', () => {
    const sem = calculateSemester([techCourse, genEdCourse, satCourse]);
    expect(sem.total_credits).toBe(7.0);
    // Tech average should be only SEC320 (90%)
    expect(sem.technical_current_average).toBe(90.0);
    // Overall average should be weighted average of SEC320 (90%) and PSY262 (70%) = 80.0%
    expect(sem.overall_current_average).toBe(80.0);
    // Cumulative GPA: SEC320 (90% = A+ = 4.0), PSY262 (70% = B = 3.0) -> (4.0*3 + 3.0*3) / 6 = 3.5
    expect(sem.cumulative_gpa).toBe(3.5);
  });
});

describe('What-If Target Calculation', () => {
  it('correctly calculates required score on remaining deliverables', () => {
    const calcResult = {
      course_code: 'TEST',
      completed_weight: 40.0,
      earned_weight: 32.0, // 80% current average
      current_average: 80.0,
      projected_final: 80.0,
      letter_grade: 'A',
      gpa_points: 4.0,
      hurdle_passed: true,
      hurdle_warnings: []
    };

    // Remaining weight is 60%. Target is 80%.
    // Points needed = 80 - 32 = 48. Required avg = 48 / 60 = 80%.
    const whatIf = calculateWhatIf(calcResult, 80);
    expect(whatIf.remainingWeight).toBe(60.0);
    expect(whatIf.requiredAvg).toBe(80.0);
    expect(whatIf.feasibility).toBe('Achievable');

    // Target is 95% (A+) -> points needed = 95 - 32 = 63. Required avg = 63 / 60 = 105% (Impossible)
    const whatIfImpossible = calculateWhatIf(calcResult, 95);
    expect(whatIfImpossible.feasibility).toBe('Impossible');
  });
});
