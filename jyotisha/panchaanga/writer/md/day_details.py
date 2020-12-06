#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from io import StringIO
from math import ceil

from indic_transliteration import sanscript
from jyotisha.panchaanga.temporal import names, interval
from jyotisha.panchaanga.temporal.names import translate_or_transliterate
from jyotisha.panchaanga.temporal import AngaType
from jyotisha.panchaanga.temporal.festival import rules
from jyotisha.panchaanga.temporal.festival.rules import RulesRepo
from jyotisha.panchaanga.temporal.time import Hour

logging.basicConfig(
  level=logging.DEBUG,
  format="%(levelname)s: %(asctime)s  %(filename)s:%(lineno)d : %(message)s "
)


def day_summary(d, panchaanga, script):
  daily_panchaanga = panchaanga.daily_panchaangas_sorted()[d]
  lunar_month_str = names.get_chandra_masa(month=daily_panchaanga.lunar_month_sunrise.index, script=script)
  solar_month_str = names.NAMES['RASHI_NAMES']['sa'][script][daily_panchaanga.solar_sidereal_date_sunset.month]
  tropical_month_str = names.NAMES['RTU_MASA_NAMES_SHORT']['sa'][script][daily_panchaanga.tropical_date_sunset.month]
  lunar_position = "%s-%s" % (names.NAMES['RASHI_NAMES']['sa'][script][daily_panchaanga.sunrise_day_angas.raashis_with_ends[0].anga.index], names.NAMES['NAKSHATRA_NAMES']['sa'][script][daily_panchaanga.sunrise_day_angas.nakshatras_with_ends[0].anga.index])
  solar_position = "%s-%s" % (solar_month_str, names.NAMES['NAKSHATRA_NAMES']['sa'][script][daily_panchaanga.sunrise_day_angas.solar_nakshatras_with_ends[0].anga.index])
  title = '%s-%s,%s🌛🌌◢◣%s-%s🌌🌞◢◣%s-%s🪐🌞' % (
    lunar_month_str, str(daily_panchaanga.get_date(month_type=RulesRepo.LUNAR_MONTH_DIR)), lunar_position,
    solar_position, str(daily_panchaanga.solar_sidereal_date_sunset), tropical_month_str,
    str(daily_panchaanga.tropical_date_sunset))

  output_stream = StringIO()
  tz = daily_panchaanga.city.get_timezone_obj()
  # Assign samvatsara, ayana, rtu #
  ayanam_sidereal = names.NAMES['AYANA_NAMES']['sa'][script][daily_panchaanga.solar_sidereal_date_sunset.month]
  ayanam = names.NAMES['AYANA_NAMES']['sa'][script][daily_panchaanga.tropical_date_sunset.month]
  rtu_solar = names.NAMES['RTU_NAMES']['sa'][script][daily_panchaanga.solar_sidereal_date_sunset.month]
  rtu_tropical = names.NAMES['RTU_NAMES']['sa'][script][daily_panchaanga.tropical_date_sunset.month]
  rtu_lunar = names.NAMES['RTU_NAMES']['sa'][script][int(ceil(daily_panchaanga.lunar_month_sunrise.index))]

  month_end_str = ''
  if daily_panchaanga.solar_sidereal_date_sunset.month_transition is None:
    month_end_str = ''
  # TODO: Fix and enable below.
  # else:
  #   _m = daily_panchaangas[d - 1].solar_sidereal_date_sunset.month
  #   if daily_panchaanga.solar_sidereal_date_sunset.month_transition >= daily_panchaanga.jd_next_sunrise:
  #     month_end_str = '%s►%s' % (names.NAMES['RASHI_NAMES'][language][_m],
  #                                Hour(24 * (
  #                                    daily_panchaanga.solar_sidereal_date_sunset.month_transition - daily_panchaanga.julian_day_start + 1)).toString(
  #                                ))
  #   else:
  #     month_end_str = '%s►%s' % (names.NAMES['RASHI_NAMES'][language][_m],
  #                                Hour(
  #                                  24 * (
  #                                        daily_panchaanga.solar_sidereal_date_sunset.month_transition - daily_panchaanga.julian_day_start)).toString(
  #                                ))
  if month_end_str == '':
    month_data = '%s (%s %d)' % (
      names.NAMES['RASHI_NAMES']['sa'][script][daily_panchaanga.solar_sidereal_date_sunset.month],
      translate_or_transliterate('दिनम्', script, source_script=sanscript.DEVANAGARI), daily_panchaanga.solar_sidereal_date_sunset.day)
  else:
    month_data = '%s (%s %d); %s' % (
      names.NAMES['RASHI_NAMES']['sa'][script][daily_panchaanga.solar_sidereal_date_sunset.month],
      translate_or_transliterate('दिनम्', script, source_script=sanscript.DEVANAGARI), daily_panchaanga.solar_sidereal_date_sunset.day, month_end_str)
  # TODO: renable below and related code further down (look for yname_lunar)
  # if yname_lunar == yname_solar:
  #   print('*' + getName('saMvatsaraH', language) + '*—%s' % yname_lunar, file=output_stream)
  #   print('*' + getName('ayanam', language) + '*—%s' % ayanam, file=output_stream)
  print("___________________", file=output_stream)
  print('- 🪐🌞**%s** — %s %s' % (translate_or_transliterate('ऋतुमानम्', script, source_script=sanscript.DEVANAGARI), rtu_tropical, ayanam), file=output_stream)
  print('- 🌌🌞**%s** — %s %s' % (translate_or_transliterate('सौरमानम्', script, source_script=sanscript.DEVANAGARI), rtu_solar, ayanam_sidereal), file=output_stream)
  print('- 🌛**%s** — %s %s' % (translate_or_transliterate('चान्द्रमानम्', script, source_script=sanscript.DEVANAGARI), rtu_lunar, lunar_month_str), file=output_stream)
  # if yname_lunar != yname_solar:
  #   print('*' + getName('saMvatsaraH', language) + '*—%s' % yname_solar, file=output_stream)
  #   print('*' + getName('ayanam', language) + '*—%s' % ayanam, file=output_stream)
  # if yname_lunar != yname_solar:
  #   print('*' + getName('saMvatsaraH', language) + '*—%s' % yname_lunar, file=output_stream)
  #   print('*' + getName('ayanam', language) + '*—%s' % ayanam, file=output_stream)
  print("___________________", file=output_stream)
  print("### %s" % (names.translate_or_transliterate(text="खचक्रस्थितिः", script=script)), file=output_stream)
  tithi_data_str = daily_panchaanga.sunrise_day_angas.get_anga_data_str(anga_type=AngaType.TITHI, script=script, reference_jd=daily_panchaanga.julian_day_start)
  print('- |🌞-🌛|%s  ' % (tithi_data_str), file=output_stream)
  vara = names.NAMES['VARA_NAMES']['sa'][script][daily_panchaanga.date.get_weekday()]
  print('- **%s**—%s  ' % (translate_or_transliterate('वासरः', script, source_script=sanscript.DEVANAGARI), vara), file=output_stream)
  nakshatra_data_str = daily_panchaanga.sunrise_day_angas.get_anga_data_str(anga_type=AngaType.NAKSHATRA, script=script, reference_jd=daily_panchaanga.julian_day_start)
  chandrashtama_rashi_data_str, rashi_data_str = get_raashi_data_str(daily_panchaanga, script)
  print('- 🌌🌛%s (%s)  ' % (nakshatra_data_str, rashi_data_str), file=output_stream)
  solar_nakshatra_str = daily_panchaanga.sunrise_day_angas.get_anga_data_str(anga_type=AngaType.SOLAR_NAKSH, script=script, reference_jd=daily_panchaanga.julian_day_start)
  print('- 🌌🌞%s  ' % (solar_nakshatra_str), file=output_stream)
  print("___________________", file=output_stream)
  yoga_data_str = daily_panchaanga.sunrise_day_angas.get_anga_data_str(anga_type=AngaType.YOGA, script=script, reference_jd=daily_panchaanga.julian_day_start)
  print('- 🌛+🌞%s  ' % (yoga_data_str), file=output_stream)
  karana_data_str = daily_panchaanga.sunrise_day_angas.get_anga_data_str(anga_type=AngaType.KARANA, script=script, reference_jd=daily_panchaanga.julian_day_start)
  print('- २|🌛-🌞|%s  ' % (karana_data_str), file=output_stream)
  print('- 🌌🌛%s  ' % (chandrashtama_rashi_data_str), file=output_stream)
  print("### %s" % (names.translate_or_transliterate(text="दिनमान-कालविभागाः", script=script)), file=output_stream)
  add_sun_moon_rise_info(daily_panchaanga, output_stream, script)

  if panchaanga.computation_system.festival_options.set_lagnas:
    lagna_data_str = get_lagna_data_str(daily_panchaanga, script)
    print('- %s  ' % (lagna_data_str), file=output_stream)


  print("___________________", file=output_stream)
  intervals = daily_panchaanga.day_length_based_periods.eight_fold_division.get_virile_intervals()
  print('- 🌞⚝%s— %s  ' % (translate_or_transliterate('भट्टभास्कर-मते वीर्यवन्तः', script, source_script=sanscript.DEVANAGARI), interval.intervals_to_md(intervals=intervals, script=script, tz=tz)),
        file=output_stream)
  intervals = daily_panchaanga.day_length_based_periods.fifteen_fold_division.get_virile_intervals()
  print('- 🌞⚝%s— %s  ' % (translate_or_transliterate('सायण-मते वीर्यवन्तः', script, source_script=sanscript.DEVANAGARI), interval.intervals_to_md(intervals=intervals, script=script, tz=tz)),
        file=output_stream)
  intervals = [daily_panchaanga.day_length_based_periods.fifteen_fold_division.braahma, daily_panchaanga.day_length_based_periods.fifteen_fold_division.madhyaraatri]
  print('- 🌞%s— %s  ' % (translate_or_transliterate('कालान्तरम्', script, source_script=sanscript.DEVANAGARI), interval.intervals_to_md(intervals=intervals, script=script, tz=tz)),
        file=output_stream)
  print("___________________", file=output_stream)

  add_raahu_yama_gulika_info(daily_panchaanga, output_stream, script)

  print("___________________", file=output_stream)
  add_shuula_info(daily_panchaanga, output_stream, script)
  print("___________________", file=output_stream)

  output_text = output_stream.getvalue()
  return (title, output_text)


def add_raahu_yama_gulika_info(daily_panchaanga, output_stream, script):
  tz = daily_panchaanga.city.get_timezone_obj()
  intervals = daily_panchaanga.day_length_based_periods.eight_fold_division.get_raahu_yama_gulikaa()
  print('- %s  ' % (interval.intervals_to_md(intervals=intervals, script=script, tz=tz)),
        file=output_stream)


def add_shuula_info(daily_panchaanga, output_stream, script):
  tz = daily_panchaanga.city.get_timezone_obj()
  shulam_end_jd = daily_panchaanga.jd_sunrise + (daily_panchaanga.jd_sunset - daily_panchaanga.jd_sunrise) * (
      names.SHULAM[daily_panchaanga.date.get_weekday()][1] / 30)
  print('- **%s**—%s (►%s); **%s**–%s  ' % (
    translate_or_transliterate('शूलम्', script, source_script=sanscript.DEVANAGARI),
    translate_or_transliterate(names.SHULAM[daily_panchaanga.date.get_weekday()][0], script, source_script=sanscript.DEVANAGARI),
    tz.julian_day_to_local_time(shulam_end_jd).get_hour_str(),
    translate_or_transliterate('परिहारः', script, source_script=sanscript.DEVANAGARI),
    translate_or_transliterate(names.SHULAM[daily_panchaanga.date.get_weekday()][2], script, source_script=sanscript.DEVANAGARI)),
        file=output_stream)


def add_sun_moon_rise_info(daily_panchaanga, output_stream, script):
  tz = daily_panchaanga.city.get_timezone_obj()
  # We prefer using Hour() below so as to differentiate post-midnight times.
  moonrise = tz.julian_day_to_local_time(daily_panchaanga.jd_moonrise).get_hour_str(reference_date=daily_panchaanga.date)
  moonset = tz.julian_day_to_local_time(daily_panchaanga.jd_moonset).get_hour_str(reference_date=daily_panchaanga.date)
  if daily_panchaanga.jd_moonrise > daily_panchaanga.jd_next_sunrise:
    moonrise = '---'
  if daily_panchaanga.jd_moonset > daily_panchaanga.jd_next_sunrise:
    moonset = '---'

  sunrise = tz.julian_day_to_local_time(daily_panchaanga.jd_sunrise).get_hour_str()
  sunset = tz.julian_day_to_local_time(daily_panchaanga.jd_sunset).get_hour_str()
  midday = tz.julian_day_to_local_time(daily_panchaanga.day_length_based_periods.aparaahna.jd_start).get_hour_str()
  print('- 🌅**%s**—%s-%s🌞️-%s🌇  ' % (translate_or_transliterate('सूर्योदयः', script, source_script=sanscript.DEVANAGARI),
                                        sunrise, midday,
                                        sunset),
        file=output_stream)
  if daily_panchaanga.jd_moonrise < daily_panchaanga.jd_moonset:
    print('- 🌛**%s**—%s; **%s**—%s  ' % (
      translate_or_transliterate('चन्द्रोदयः', script, source_script=sanscript.DEVANAGARI), moonrise,
      translate_or_transliterate('चन्द्रास्तमयः', script, source_script=sanscript.DEVANAGARI), moonset),
          file=output_stream)
  else:
    print('- 🌛**%s**—%s; **%s**—%s  ' % (
      translate_or_transliterate('चन्द्रास्तमयः', script, source_script=sanscript.DEVANAGARI), moonset,
      translate_or_transliterate('चन्द्रोदयः', script, source_script=sanscript.DEVANAGARI), moonrise),
          file=output_stream)


def get_raashi_data_str(daily_panchaanga, script):
  jd = daily_panchaanga.julian_day_start
  chandrashtama_rashi_data_str = ''
  for raashi_span in daily_panchaanga.sunrise_day_angas.raashis_with_ends:
    (rashi_ID, rashi_end_jd) = (raashi_span.anga.index, raashi_span.jd_end)
    rashi = names.NAMES['RASHI_NAMES']['sa'][script][rashi_ID]
    if rashi_end_jd is None:
      rashi_data_str = '%s' % (rashi)
      chandrashtama_rashi_data_str = '- **%s**—%s' % (translate_or_transliterate('चन्द्राष्टम-राशिः', script, source_script=sanscript.DEVANAGARI),
                                                      names.NAMES['RASHI_NAMES']['sa'][script][((rashi_ID - 8) % 12) + 1])
    else:
      rashi_data_str = '%s►%s' % (
        rashi, Hour(24 * (rashi_end_jd - jd)).to_string())
      chandrashtama_rashi_data_str = '- **%s**—%s►%s; %s ➥' % (
        translate_or_transliterate('चन्द्राष्टम-राशिः', script, source_script=sanscript.DEVANAGARI),
        names.NAMES['RASHI_NAMES']['sa'][script][((rashi_ID - 8) % 12) + 1],
        Hour(24 * (rashi_end_jd - jd)).to_string(),
        names.NAMES['RASHI_NAMES']['sa'][script][((rashi_ID - 7) % 12) + 1])
  return chandrashtama_rashi_data_str, rashi_data_str


def get_lagna_data_str(daily_panchaanga, script):
  jd = daily_panchaanga.julian_day_start
  lagna_data_str = ''
  for lagna_ID, lagna_end_jd in daily_panchaanga.lagna_data:
    lagna = names.NAMES['RASHI_NAMES']['sa'][script][lagna_ID]
    lagna_data_str = '%s; %s►%s' % \
                     (lagna_data_str, lagna,
                      Hour(24 * (lagna_end_jd - jd)).to_string(
                      ))
  lagna_data_str = '*' + translate_or_transliterate('लग्नम्', script, source_script=sanscript.DEVANAGARI) + '*—' + lagna_data_str[2:]
  return lagna_data_str



def get_festivals_md(daily_panchaanga, panchaanga, languages, scripts):
  rules_collection = rules.RulesCollection.get_cached(
    repos_tuple=tuple(panchaanga.computation_system.festival_options.repos))
  fest_details_dict = rules_collection.name_to_rule
  output_stream = StringIO()
  for f in sorted(daily_panchaanga.festival_id_to_instance.values()):
    print('%s' % (f.md_code(languages=languages, scripts=scripts, timezone=panchaanga.city.get_timezone_obj(),
                fest_details_dict=fest_details_dict)), file=output_stream)
  return output_stream.getvalue()