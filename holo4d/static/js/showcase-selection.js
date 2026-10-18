/* Editorial selection only. Existing inference, overlays and metric roots stay
 * unchanged. Exact source IDs prevent pairing unrelated robot recordings.
 */
const holo4dGupta = 'robot/GuptaLab__failure__2023-04-20__Thu_Apr_20_14-22-26_2023__static_1__22246076';
const holo4dRad = 'robot/RAD__success__2023-08-31__Thu_Aug_31_13-55-38_2023__static_2__35215462';
const holo4dTriSep = 'robot/TRI__failure__2023-09-21__Thu_Sep_21_10-05-35_2023__static_2__25947356';
const holo4dTriOct = 'robot/TRI__failure__2023-10-23__Mon_Oct_23_14-34-51_2023__static_1__20252535';

window.HOLO4D_SHOWCASE = Object.freeze({
  robots: [
    ['robot/figure_0__window00__start00000', 'subject_orbit_zoom', 'vggt_omega_cowtracker'],
    ['robot/figure_0__window00__start00000', 'slow_crane_dolly_in', 'vggt_omega_cowtracker'],
    ['robot/tesla_0__window02__start00048', 'vista4d_avocado_slice__close_crane_above', 'vggt_omega_cowtracker'],
    ['robot/tesla_0__window02__start00048', 'vista4d_avocado_slice__left_front_zoom', 'vggt_omega_cowtracker'],
    ['robot/figure_1__window00__start00000', 'vista4d_avocado_slice__close_crane_above', 'vggt_omega_cowtracker'],
    ['robot/figure_1__window00__start00000', 'subject_orbit_zoom', 'vggt_omega_cowtracker'],
    [holo4dGupta, 'static_left_front', '4rc'],
    [holo4dGupta, 'static_right_front', '4rc'],
    [holo4dTriSep, 'vista4d_avocado_slice__close_crane_above', '4rc'],
    [holo4dTriSep, 'vista4d_avocado_slice__left_front_zoom', '4rc'],
    [holo4dRad, 'static_right', '4rc'],
    [holo4dRad, 'vista4d_avocado_slice__close_crane_above', '4rc'],
    [holo4dTriOct, 'safe_other_side_left_60_r80_fixedheight', '4rc'],
    [holo4dTriOct, 'safe_high_center_65_r80_fixedheight', '4rc']
  ],
  reshooting: [
    ['native110/camera-lens', 'crane-zoom', 'vggt_omega_cowtracker'],
    ['native110/camera-lens', 'side-full', 'vggt_omega_cowtracker'],
    ['native110/fashion-walk', 'arc-left-right', 'vggt_omega_cowtracker'],
    ['native110/fashion-walk', 'crane-above', 'vggt_omega_cowtracker'],
    ['native110/golf', 'dolly-out', 'vggt_omega_cowtracker'],
    ['native110/golf', 'dolly-in', 'vggt_omega_cowtracker'],
    ['native110/drive-desert', 'side-fly', 'vggt_omega_cowtracker'],
    ['native110/drive-desert', 'back-follow', 'vggt_omega_cowtracker'],
    ['native110/friends-restaurant', 'side-dolly', 'vggt_omega_cowtracker'],
    ['native110/friends-restaurant', 'crane-below', 'vggt_omega_cowtracker'],
    ['davis/camel', 'orbit_left', '4rc'],
    ['davis/camel', 'zoom_in', '4rc'],
    ['davis/kite-surf', 'pan_left', '4rc'],
    ['davis/kite-surf', 'translate_right', '4rc']
  ],
  // Long videos: humanoid pairs first, then manipulation; ids are exact export paths.
  long: [
    'long_robot/figure_1__window00__start00000/vista4d_avocado_slice__close_crane_above',
    'long_robot/figure_1__window00__start00000/subject_orbit_zoom',
    'long_robot/tesla_0__window02__start00048/bed_zoom_inout',
    'long_robot/tesla_0__window02__start00048/subject_orbit_zoom',
    'long_robot/GuptaLab__failure__2023-04-20__Thu_Apr_20_14-22-26_2023__static_1__22246076/static_left_front',
    'long_robot/GuptaLab__failure__2023-04-20__Thu_Apr_20_14-22-26_2023__static_1__22246076/static_right_front'
  ],
  comparisons: [
    'comparison/golf/dolly-out',
    'comparison/drive-desert/side-fly',
    'comparison/drive-desert/back-follow',
    'comparison/friends-restaurant/side-dolly',
    'comparison/fashion-walk/arc-left-right',
    'comparison/snow-dog/crane-above',
    'comparison/mountain-hike/truck-crane-below',
    'comparison/woman-beach/crane-above',
    'comparison/truck-pose/left-right'
  ]
});

function holo4dSelectShowcase(entries, section) {
  const picks = window.HOLO4D_SHOWCASE[section];
  if (!picks) return entries;
  return picks.map(pick => {
    const matches = entries.filter(entry => typeof pick === 'string'
      ? entry.id === pick
      : entry.scene_id === pick[0] && entry.trajectory_id === pick[1] && entry.backend === pick[2]);
    if (matches.length !== 1 || matches[0].review_pending) {
      throw new Error(`Unverified or ambiguous Holo4D showcase entry: ${JSON.stringify(pick)}`);
    }
    return matches[0];
  });
}
