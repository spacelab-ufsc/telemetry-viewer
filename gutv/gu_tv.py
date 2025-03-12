# -*- coding: utf-8 -*-

#
#  gu_tv.py
#  
#  Copyright The GOLDS-UFSC Telemetry Viewer Contributors.
#  
#  This file is part of GOLDS-UFSC Telemetry Viewer.
#
#  GOLDS-UFSC Telemetry Viewer is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  GOLDS-UFSC Telemetry Viewer is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with GOLDS-UFSC Telemetry Viewer; if not, see
#  <http://www.gnu.org/licenses/>.
#  
#

import os
import json
import socket
import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

import gutv.version
import gutv.convert

# UI File
_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__file__)) + '/data/ui/gutv.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/gutv/gutv.glade'

# Icon File
_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/gutv_256x256.png'
_ICON_FILE_LINUX_SYSTEM         = '/usr/share/icons/gutv_256x256.png'

# Logo File
_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab-logo-full-400x200.png'
_LOGO_FILE_LINUX_SYSTEM         = '/usr/share/spacelab_decoder/spacelab-logo-full-400x200.png'

class GUTV:

    def __init__(self):
        """
        Main class constructor.

        :return: None
        """
        self.builder = Gtk.Builder()

        # UI file from Glade
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.builder.connect_signals(self)

        self._build_widgets()

        self._server_socket = None

    def _build_widgets(self):
        # Main window
        self.window = self.builder.get_object("window_main")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.set_wmclass(self.window.get_title(), self.window.get_title())
        self.window.connect("destroy", Gtk.main_quit)

        # Toolbar
        self.button_preferences         = self.builder.get_object("button_preferences")
        self.entry_address              = self.builder.get_object("entry_address")
        self.entry_port                 = self.builder.get_object("entry_port")
        self.button_open_socket         = self.builder.get_object("button_open_socket")
        self.button_open_socket.connect("clicked", self.on_button_open_socket_clicked)
        self.button_close_socket        = self.builder.get_object("button_close_socket")
        self.button_close_socket.connect("clicked", self.on_button_close_socket_clicked)

        # EPS tab
        self.label_eps_mcu_date             = self.builder.get_object("label_eps_mcu_date")
        self.label_eps_mcu_time             = self.builder.get_object("label_eps_mcu_time")
        self.label_eps_mcu_temp             = self.builder.get_object("label_eps_mcu_temp")
        self.label_eps_mcu_curr             = self.builder.get_object("label_eps_mcu_curr")
        self.label_eps_mcu_last_reset_cause = self.builder.get_object("label_eps_mcu_last_reset_cause")
        self.label_eps_mcu_reset_count      = self.builder.get_object("label_eps_mcu_reset_count")
        self.label_eps_sp_volt_mypx         = self.builder.get_object("label_eps_sp_volt_mypx")
        self.label_eps_sp_volt_mxpz         = self.builder.get_object("label_eps_sp_volt_mxpz")
        self.label_eps_sp_volt_mzpy         = self.builder.get_object("label_eps_sp_volt_mzpy")
        self.label_eps_sp_curr_mx           = self.builder.get_object("label_eps_sp_curr_mx")
        self.label_eps_sp_curr_px           = self.builder.get_object("label_eps_sp_curr_px")
        self.label_eps_sp_curr_my           = self.builder.get_object("label_eps_sp_curr_my")
        self.label_eps_sp_curr_py           = self.builder.get_object("label_eps_sp_curr_py")
        self.label_eps_sp_curr_mz           = self.builder.get_object("label_eps_sp_curr_mz")
        self.label_eps_sp_curr_pz           = self.builder.get_object("label_eps_sp_curr_pz")
        self.label_eps_mppt_dc_ch_1         = self.builder.get_object("label_eps_mppt_dc_ch_1")
        self.label_eps_mppt_dc_ch_2         = self.builder.get_object("label_eps_mppt_dc_ch_2")
        self.label_eps_mppt_dc_ch_3         = self.builder.get_object("label_eps_mppt_dc_ch_3")
        self.label_eps_mppt_mode_ch_1       = self.builder.get_object("label_eps_mppt_mode_ch_1")
        self.label_eps_mppt_mode_ch_2       = self.builder.get_object("label_eps_mppt_mode_ch_2")
        self.label_eps_mppt_mode_ch_3       = self.builder.get_object("label_eps_mppt_mode_ch_3")
        self.label_eps_mppt_output_volt     = self.builder.get_object("label_eps_mppt_output_volt")
        self.label_eps_rtd_ch_0             = self.builder.get_object("label_eps_rtd_ch_0")
        self.label_eps_rtd_ch_1             = self.builder.get_object("label_eps_rtd_ch_1")
        self.label_eps_rtd_ch_2             = self.builder.get_object("label_eps_rtd_ch_2")
        self.label_eps_rtd_ch_3             = self.builder.get_object("label_eps_rtd_ch_3")
        self.label_eps_rtd_ch_4             = self.builder.get_object("label_eps_rtd_ch_4")
        self.label_eps_rtd_ch_5             = self.builder.get_object("label_eps_rtd_ch_5")
        self.label_eps_rtd_ch_6             = self.builder.get_object("label_eps_rtd_ch_6")
        self.label_eps_bat_volt             = self.builder.get_object("label_eps_bat_volt")
        self.label_eps_bat_curr             = self.builder.get_object("label_eps_bat_curr")
        self.label_eps_bat_average_curr     = self.builder.get_object("label_eps_bat_average_curr")
        self.label_eps_bat_acc_curr         = self.builder.get_object("label_eps_bat_acc_curr")
        self.label_eps_bat_charge           = self.builder.get_object("label_eps_bat_charge")
        self.label_eps_bat_heater_1_dc      = self.builder.get_object("label_eps_bat_heater_1_dc")
        self.label_eps_bat_heater_2_dc      = self.builder.get_object("label_eps_bat_heater_2_dc")
        self.label_eps_bat_heater_1_mode    = self.builder.get_object("label_eps_bat_heater_1_mode")
        self.label_eps_bat_heater_2_mode    = self.builder.get_object("label_eps_bat_heater_2_mode")
        self.label_eps_bat_temp_monitor     = self.builder.get_object("label_eps_bat_temp_monitor")
        self.label_eps_bat_status           = self.builder.get_object("label_eps_bat_status")
        self.label_eps_bat_protection       = self.builder.get_object("label_eps_bat_protection")
        self.label_eps_bat_cycle_counter    = self.builder.get_object("label_eps_bat_cycle_counter")
        self.label_eps_bat_raac             = self.builder.get_object("label_eps_bat_raac")
        self.label_eps_bat_rsac             = self.builder.get_object("label_eps_bat_rsac")
        self.label_eps_bat_rarc             = self.builder.get_object("label_eps_bat_rarc")
        self.label_eps_bat_rsrc             = self.builder.get_object("label_eps_bat_rsrc")

        # OBDH
        self.label_obdh_mcu_date                    = self.builder.get_object("label_obdh_mcu_date")
        self.label_obdh_mcu_time                    = self.builder.get_object("label_obdh_mcu_time")
        self.label_obdh_mcu_temp                    = self.builder.get_object("label_obdh_mcu_temp")
        self.label_obdh_mcu_last_reset_cause        = self.builder.get_object("label_obdh_mcu_last_reset_cause")
        self.label_obdh_mcu_reset_count             = self.builder.get_object("label_obdh_mcu_reset_count")
        self.label_obdh_general_voltage             = self.builder.get_object("label_obdh_general_voltage")
        self.label_obdh_general_current             = self.builder.get_object("label_obdh_general_current")
        self.label_obdh_mem_sec_obdh                = self.builder.get_object("label_obdh_mem_sec_obdh")
        self.label_obdh_mem_sec_eps                 = self.builder.get_object("label_obdh_mem_sec_eps")
        self.label_obdh_mem_sec_ttc_0               = self.builder.get_object("label_obdh_mem_sec_ttc_0")
        self.label_obdh_mem_sec_ttc_1               = self.builder.get_object("label_obdh_mem_sec_ttc_1")
        self.label_obdh_mem_sec_antenna             = self.builder.get_object("label_obdh_mem_sec_antenna")
        self.label_obdh_mem_sec_edc                 = self.builder.get_object("label_obdh_mem_sec_edc")
        self.label_obdh_mem_sec_payloadx            = self.builder.get_object("label_obdh_mem_sec_payloadx")
        self.label_obdh_mem_sec_sbcd                = self.builder.get_object("label_obdh_mem_sec_sbcd")
        self.label_obdh_position_lattitude          = self.builder.get_object("label_obdh_position_lattitude")
        self.label_obdh_position_longitude          = self.builder.get_object("label_obdh_position_longitude")
        self.label_obdh_position_altitude           = self.builder.get_object("label_obdh_position_altitude")
        self.label_obdh_position_date               = self.builder.get_object("label_obdh_position_date")
        self.label_obdh_position_time               = self.builder.get_object("label_obdh_position_time")
        self.textview_obdh_position_tle             = self.builder.get_object("textview_obdh_position_tle")
        self.textbuffer_obdh_position_tle           = self.textview_obdh_position_tle.get_buffer()
        self.label_obdh_position_date               = self.builder.get_object("label_obdh_position_date")
        self.label_obdh_position_time               = self.builder.get_object("label_obdh_position_time")
        self.label_obdh_op_last_valid_tc            = self.builder.get_object("label_obdh_op_last_valid_tc")
        self.label_obdh_op_mode                     = self.builder.get_object("label_obdh_op_mode")
        self.label_obdh_op_date_last_mode_change    = self.builder.get_object("label_obdh_op_date_last_mode_change")
        self.label_obdh_op_time_last_mode_change    = self.builder.get_object("label_obdh_op_time_last_mode_change")
        self.label_obdh_op_mode_duration            = self.builder.get_object("label_obdh_op_mode_duration")
        self.label_obdh_op_initial_hib              = self.builder.get_object("label_obdh_op_initial_hib")
        self.label_obdh_op_initial_hib_time         = self.builder.get_object("label_obdh_op_initial_hib_time")
        self.label_obdh_op_manual_mode              = self.builder.get_object("label_obdh_op_manual_mode")
        self.label_obdh_op_main_edc                 = self.builder.get_object("label_obdh_op_main_edc")
        self.label_obdh_op_general_tm               = self.builder.get_object("label_obdh_op_general_tm")
        self.label_obdh_op_main_pl_state            = self.builder.get_object("label_obdh_op_main_pl_state")
        self.label_obdh_op_secondary_pl_state       = self.builder.get_object("label_obdh_op_secondary_pl_state")
        self.label_obdh_op_date_last_reading        = self.builder.get_object("label_obdh_op_date_last_reading")
        self.label_obdh_op_time_last_reading        = self.builder.get_object("label_obdh_op_time_last_reading")
        self.label_obdh_op_remaining_hib_time       = self.builder.get_object("label_obdh_op_remaining_hib_time")

        # TTC
        self.label_ttc_mcu1_date                    = self.builder.get_object("label_ttc_mcu1_date")
        self.label_ttc_mcu1_time                    = self.builder.get_object("label_ttc_mcu1_time")
        self.label_ttc_mcu1_temp                    = self.builder.get_object("label_ttc_mcu1_temp")
        self.label_ttc_mcu1_last_rst_cause          = self.builder.get_object("label_ttc_mcu1_last_rst_cause")
        self.label_ttc_mcu1_rst_count               = self.builder.get_object("label_ttc_mcu1_rst_count")
        self.label_ttc_mcu1_volt                    = self.builder.get_object("label_ttc_mcu1_volt")
        self.label_ttc_mcu1_curr                    = self.builder.get_object("label_ttc_mcu1_curr")
        self.label_ttc_radio1_volt                  = self.builder.get_object("label_ttc_radio1_volt")
        self.label_ttc_radio1_curr                  = self.builder.get_object("label_ttc_radio1_curr")
        self.label_ttc_radio1_temp                  = self.builder.get_object("label_ttc_radio1_temp")
        self.label_ttc_radio1_tx_en                 = self.builder.get_object("label_ttc_radio1_tx_en")
        self.label_ttc_radio1_count                 = self.builder.get_object("label_ttc_radio1_count")
        self.label_ttc_mcu1_date                    = self.builder.get_object("label_ttc_mcu1_date")
        self.label_ttc_mcu1_time                    = self.builder.get_object("label_ttc_mcu1_time")
        self.label_ttc_mcu1_temp                    = self.builder.get_object("label_ttc_mcu1_temp")
        self.label_ttc_mcu1_last_rst_cause          = self.builder.get_object("label_ttc_mcu1_last_rst_cause")
        self.label_ttc_mcu1_rst_count               = self.builder.get_object("label_ttc_mcu1_rst_count")
        self.label_ttc_mcu1_volt                    = self.builder.get_object("label_ttc_mcu1_volt")
        self.label_ttc_mcu1_curr                    = self.builder.get_object("label_ttc_mcu1_curr")
        self.label_ttc_radio2_volt                  = self.builder.get_object("label_ttc_radio2_volt")
        self.label_ttc_radio2_curr                  = self.builder.get_object("label_ttc_radio2_curr")
        self.label_ttc_radio2_temp                  = self.builder.get_object("label_ttc_radio2_temp")
        self.label_ttc_radio2_tx_en                 = self.builder.get_object("label_ttc_radio2_tx_en")
        self.label_ttc_radio2_tx_count              = self.builder.get_object("label_ttc_radio2_tx_count")
        self.label_ttc_radio2_rx_count              = self.builder.get_object("label_ttc_radio2_rx_count")

        # Antenna
        self.label_ant_temp                         = self.builder.get_object("label_ant_temp")
        self.label_ant_temp                         = self.builder.get_object("label_ant_temp")
        self.label_ant_deployment_exec              = self.builder.get_object("label_ant_deployment_exec")
        self.label_ant_deployment_count             = self.builder.get_object("label_ant_deployment_count")
        self.label_ant_indep_burn                   = self.builder.get_object("label_ant_indep_burn")
        self.label_ant_ignore_switches              = self.builder.get_object("label_ant_ignore_switches")
        self.label_ant_armed                        = self.builder.get_object("label_ant_armed")
        self.label_ant_mp1_deployed                 = self.builder.get_object("label_ant_mp1_deployed")
        self.label_ant_mp1_dep_stop                 = self.builder.get_object("label_ant_mp1_dep_stop")
        self.label_ant_mp1_dep_sys                  = self.builder.get_object("label_ant_mp1_dep_sys")
        self.label_ant_mp2_deployed                 = self.builder.get_object("label_ant_mp2_deployed")
        self.label_ant_mp2_dep_stop                 = self.builder.get_object("label_ant_mp2_dep_stop")
        self.label_ant_mp2_dep_sys                  = self.builder.get_object("label_ant_mp2_dep_sys")
        self.label_ant_mp3_deployed                 = self.builder.get_object("label_ant_mp3_deployed")
        self.label_ant_mp3_dep_stop                 = self.builder.get_object("label_ant_mp3_dep_stop")
        self.label_ant_mp3_dep_sys                  = self.builder.get_object("label_ant_mp3_dep_sys")
        self.label_ant_mp4_deployed                 = self.builder.get_object("label_ant_mp4_deployed")
        self.label_ant_mp4_dep_stop                 = self.builder.get_object("label_ant_mp4_dep_stop")
        self.label_ant_mp4_dep_sys                  = self.builder.get_object("label_ant_mp4_dep_sys")

        # EDC 1
        self.label_edc1_date                        = self.builder.get_object("label_edc1_date")
        self.label_edc1_time                        = self.builder.get_object("label_edc1_time")
        self.label_edc1_elapsed_time                = self.builder.get_object("label_edc1_elapsed_time")
        self.label_edc1_volt                        = self.builder.get_object("label_edc1_volt")
        self.label_edc1_curr_dig                    = self.builder.get_object("label_edc1_curr_dig")
        self.label_edc1_curr_ana                    = self.builder.get_object("label_edc1_curr_ana")
        self.label_edc1_temp                        = self.builder.get_object("label_edc1_temp")
        self.label_edc1_pll_sync                    = self.builder.get_object("label_edc1_pll_sync")
        self.label_edc1_adc_rms_lvl                 = self.builder.get_object("label_edc1_adc_rms_lvl")
        self.label_edc1_tot_ptt_pkg                 = self.builder.get_object("label_edc1_tot_ptt_pkg")
        self.label_edc1_ptt_dec_ch                  = self.builder.get_object("label_edc1_ptt_dec_ch")
        self.label_edc1_mss_err_count               = self.builder.get_object("label_edc1_mss_err_count")

        # EDC 2
        self.label_edc2_date                        = self.builder.get_object("label_edc2_date")
        self.label_edc2_time                        = self.builder.get_object("label_edc2_time")
        self.label_edc2_elapsed_time                = self.builder.get_object("label_edc2_elapsed_time")
        self.label_edc2_volt                        = self.builder.get_object("label_edc2_volt")
        self.label_edc2_curr_dig                    = self.builder.get_object("label_edc2_curr_dig")
        self.label_edc2_curr_ana                    = self.builder.get_object("label_edc2_curr_ana")
        self.label_edc2_temp                        = self.builder.get_object("label_edc2_temp")
        self.label_edc2_pll_sync                    = self.builder.get_object("label_edc2_pll_sync")
        self.label_edc2_adc_rms_lvl                 = self.builder.get_object("label_edc2_adc_rms_lvl")
        self.label_edc2_tot_ptt_pkg                 = self.builder.get_object("label_edc2_tot_ptt_pkg")
        self.label_edc2_ptt_dec_ch                  = self.builder.get_object("label_edc2_ptt_dec_ch")
        self.label_edc2_mss_err_count               = self.builder.get_object("label_edc2_mss_err_count")

        # About dialog
        self.aboutdialog = self.builder.get_object("aboutdialog_gutv")
        self.aboutdialog.set_version(gutv.version.__version__)
        if os.path.isfile(_LOGO_FILE_LOCAL):
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LOCAL))
        else:
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LINUX_SYSTEM))

        # About toolbutton
        self.toolbutton_about = self.builder.get_object("toolbutton_about")
        self.toolbutton_about.connect("clicked", self.on_toolbutton_about_clicked)

    def run(self):
        self.window.show_all()

        Gtk.main()

        return 0

    def destroy(window, self):
        Gtk.main_quit()

    def on_button_open_socket_clicked(self, button):
        try:
            adr = self.entry_address.get_text()
            port = int(self.entry_port.get_text())

            self._server_socket = self._create_socket_server(adr, int(port))

            if self._server_socket:
                # Monitor the socket for incoming connections using GLib's IO watch
                self._socket_io_channel = GLib.IOChannel(self._server_socket.fileno())
                GLib.io_add_watch(self._socket_io_channel, GLib.IO_IN, self._handle_new_connection)

                self.entry_address.set_sensitive(False)
                self.entry_port.set_sensitive(False)
                self.button_open_socket.set_sensitive(False)
                self.button_close_socket.set_sensitive(True)
        except socket.error as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error opening the socker server!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()

    def on_button_close_socket_clicked(self, button):
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()

        self.entry_address.set_sensitive(True)
        self.entry_port.set_sensitive(True)
        self.button_open_socket.set_sensitive(True)
        self.button_close_socket.set_sensitive(False)

    def on_toolbutton_about_clicked(self, toolbutton):
        response = self.aboutdialog.run()

        if response == Gtk.ResponseType.DELETE_EVENT:
            self.aboutdialog.hide()

    def _decode_pkt(self, pkt_json):
        data = json.loads(pkt_json)

        if "eps_timestamp" in data:
            self.label_eps_mcu_date.set_text(datetime.datetime.fromtimestamp(int(data["eps_timestamp"])).strftime('%Y/%m/%d'))
            self.label_eps_mcu_time.set_text(datetime.datetime.fromtimestamp(int(data["eps_timestamp"])).strftime('%H:%M:%S'))
#            self.label_eps_mcu_time.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 1, 0, 1))
#        else:
#            self.label_eps_mcu_time.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))

        if "eps_mcu_temp" in data:
            self.label_eps_mcu_temp.set_text(str((int(data["eps_mcu_temp"]) - 273)) + " " + "°C")

        if "eps_mcu_curr" in data:
            self.label_eps_mcu_curr.set_text(data["eps_mcu_curr"] + " " + "mA")

        if "eps_mcu_last_rst_cause" in data:
            self.label_eps_mcu_last_reset_cause.set_text(data["eps_mcu_last_rst_cause"])

        if "eps_mcu_rst_count" in data:
            self.label_eps_mcu_reset_count.set_text(data["eps_mcu_rst_count"])

        if "eps_sp_volt_mypx" in data:
            self.label_eps_sp_volt_mypx.set_text(data["eps_sp_volt_mypx"] + " " + "mV")

        if "eps_sp_volt_mxpz" in data:
            self.label_eps_sp_volt_mxpz.set_text(data["eps_sp_volt_mxpz"] + " " + "mV")

        if "eps_sp_volt_mzpy" in data:
            self.label_eps_sp_volt_mzpy.set_text(data["eps_sp_volt_mzpy"] + " " + "mV")

        if "eps_sp_curr_mx" in data:
            self.label_eps_sp_curr_mx.set_text(data["eps_sp_curr_mx"] + " " + "mA")

        if "eps_sp_curr_px" in data:
            self.label_eps_sp_curr_px.set_text(data["eps_sp_curr_px"] + " " + "mA")

        if "eps_sp_curr_my" in data:
            self.label_eps_sp_curr_my.set_text(data["eps_sp_curr_my"] + " " + "mA")

        if "eps_sp_curr_py" in data:
            self.label_eps_sp_curr_py.set_text(data["eps_sp_curr_py"] + " " + "mA")

        if "eps_sp_curr_mz" in data:
            self.label_eps_sp_curr_mz.set_text(data["eps_sp_curr_mz"] + " " + "mA")

        if "eps_sp_curr_pz" in data:
            self.label_eps_sp_curr_pz.set_text(data["eps_sp_curr_pz"] + " " + "mA")

        if "eps_mppt_1_dc" in data:
            self.label_eps_mppt_dc_ch_1.set_text(data["eps_mppt_1_dc"] + " " + "%")

        if "eps_mppt_2_dc" in data:
            self.label_eps_mppt_dc_ch_2.set_text(data["eps_mppt_2_dc"] + " " + "%")

        if "eps_mppt_3_dc" in data:
            self.label_eps_mppt_dc_ch_3.set_text(data["eps_mppt_3_dc"] + " " + "%")

        if "eps_mppt_1_mode" in data:
            if int(data["eps_mppt_1_mode"]) == 0:
                self.label_eps_mppt_mode_ch_1.set_text("Automatic")
            elif int(data["eps_mppt_1_mode"]) == 1:
                self.label_eps_mppt_mode_ch_1.set_text("Manual")
            else:
                self.label_eps_mppt_mode_ch_1.set_text("Unknown")

        if "eps_mppt_2_mode" in data:
            if int(data["eps_mppt_2_mode"]) == 0:
                self.label_eps_mppt_mode_ch_2.set_text("Automatic")
            elif int(data["eps_mppt_2_mode"]) == 1:
                self.label_eps_mppt_mode_ch_2.set_text("Manual")
            else:
                self.label_eps_mppt_mode_ch_2.set_text("Unknown")

        if "eps_mppt_3_mode" in data:
            if int(data["eps_mppt_3_mode"]) == 0:
                self.label_eps_mppt_mode_ch_3.set_text("Automatic")
            elif int(data["eps_mppt_3_mode"]) == 1:
                self.label_eps_mppt_mode_ch_3.set_text("Manual")
            else:
                self.label_eps_mppt_mode_ch_3.set_text("Unknown")

        if "eps_mppt_sp_volt" in data:
            self.label_eps_mppt_output_volt.set_text(data["eps_mppt_sp_volt"] + " " + "mV")

        if "eps_rtd_0_temp" in data:
            self.label_eps_rtd_ch_0.set_text(str(int(data["eps_rtd_0_temp"]) - 273) + " " + "°C")

        if "eps_rtd_1_temp" in data:
            self.label_eps_rtd_ch_1.set_text(str(int(data["eps_rtd_1_temp"]) - 273) + " " + "°C")

        if "eps_rtd_2_temp" in data:
            self.label_eps_rtd_ch_2.set_text(str(int(data["eps_rtd_2_temp"]) - 273) + " " + "°C")

        if "eps_rtd_3_temp" in data:
            self.label_eps_rtd_ch_3.set_text(str(int(data["eps_rtd_3_temp"]) - 273) + " " + "°C")

        if "eps_rtd_4_temp" in data:
            self.label_eps_rtd_ch_4.set_text(str(int(data["eps_rtd_4_temp"]) - 273) + " " + "°C")

        if "eps_rtd_5_temp" in data:
            self.label_eps_rtd_ch_5.set_text(str(int(data["eps_rtd_5_temp"]) - 273) + " " + "°C")

        if "eps_rtd_6_temp" in data:
            self.label_eps_rtd_ch_6.set_text(str(int(data["eps_rtd_6_temp"]) - 273) + " " + "°C")

        if "eps_bat_volt" in data:
            self.label_eps_bat_volt.set_text(data["eps_bat_volt"] + " " + "mV")

        if "eps_bat_curr" in data:
            self.label_eps_bat_curr.set_text(data["eps_bat_curr"] + " " + "mA")

        if "eps_bat_avg_curr" in data:
            self.label_eps_bat_average_curr.set_text(data["eps_bat_avg_curr"] + " " + "mA")

        if "eps_bat_acc_curr" in data:
            self.label_eps_bat_acc_curr.set_text(data["eps_bat_acc_curr"] + " " + "mA")

        if "eps_bat_charge" in data:
            self.label_eps_bat_charge.set_text(data["eps_bat_charge"] + " " + "mAh")

        if "eps_bat_heater_1_dc" in data:
            self.label_eps_bat_heater_1_dc.set_text(data["eps_bat_heater_1_dc"] + " " + "%")

        if "eps_bat_heater_2_dc" in data:
            self.label_eps_bat_heater_2_dc.set_text(data["eps_bat_heater_2_dc"] + " " + "%")

        if "eps_bat_heater_1_mode" in data:
            if int(data["eps_bat_heater_1_mode"]) == 0:
                self.label_eps_bat_heater_1_mode.set_text("Automatic")
            elif int(data["eps_bat_heater_1_mode"]) == 1:
                self.label_eps_bat_heater_1_mode.set_text("Manual")
            else:
                self.label_eps_bat_heater_1_mode.set_text("Unknown")

        if "eps_bat_heater_2_mode" in data:
            if int(data["eps_bat_heater_2_mode"]) == 0:
                self.label_eps_bat_heater_2_mode.set_text("Automatic")
            elif int(data["eps_bat_heater_2_mode"]) == 1:
                self.label_eps_bat_heater_2_mode.set_text("Manual")
            else:
                self.label_eps_bat_heater_2_mode.set_text("Unknown")

        if "eps_bat_mon_temp" in data:
            self.label_eps_bat_temp_monitor.set_text(str((int(data["eps_bat_mon_temp"]) - 273)) + " " + "°C")

#        if "eps_main_pwr_bus_volt" in data:
#            self..set_text(data["eps_main_pwr_bus_volt"] + " " + "mV")

        '''
        if "" in data:
            self.label_eps_bat_protection.set_text()

        if "" in data:
            self.label_eps_bat_cycle_counter.set_text()

        if "" in data:
            self.label_eps_bat_raac.set_text()

        if "" in data:
            self.label_eps_bat_rsac.set_text()

        if "" in data:
            self.label_eps_bat_rarc.set_text()

        if "" in data:
            self.label_eps_bat_rsrc.set_text()
        '''
        if "obdh_timestamp" in data:
            self.label_obdh_mcu_date.set_text(datetime.datetime.fromtimestamp(int(data["obdh_timestamp"])).strftime('%Y/%m/%d'))
            self.label_obdh_mcu_time.set_text(datetime.datetime.fromtimestamp(int(data["obdh_timestamp"])).strftime('%H:%M:%S'))

        if "obdh_mcu_temp" in data:
            self.label_obdh_mcu_temp.set_text(str((int(data["obdh_mcu_temp"]) - 273)) + " " + "°C")

        if "obdh_mcu_last_rst_cause" in data:
            self.label_obdh_mcu_last_reset_cause.set_text(data["obdh_mcu_last_rst_cause"])

        if "obdh_mcu_rst_count" in data:
            self.label_obdh_mcu_reset_count.set_text(data["obdh_mcu_rst_count"])

        if "obdh_volt" in data:
            self.label_obdh_general_voltage.set_text(data["obdh_volt"] + " " + "mV")

        if "obdh_curr" in data:
            self.label_obdh_general_current.set_text(data["obdh_curr"] + " " + "mA")

#        if "obdh_mem_data_log" in data:
#            self..set_text(data["obdh_mem_data_log"])

        if "obdh_mem_sec_obdh" in data:
            self.label_obdh_mem_sec_obdh.set_text(data["obdh_mem_sec_obdh"])

        if "obdh_mem_sec_eps" in data:
            self.label_obdh_mem_sec_eps.set_text(data["obdh_mem_sec_eps"])

        if "obdh_mem_sec_ttc_0" in data:
            self.label_obdh_mem_sec_ttc_0.set_text(data["obdh_mem_sec_ttc_0"])

        if "obdh_mem_sec_ttc_1" in data:
            self.label_obdh_mem_sec_ttc_1.set_text(data["obdh_mem_sec_ttc_1"])

        if "obdh_mem_sec_ant" in data:
            self.label_obdh_mem_sec_antenna.set_text(data["obdh_mem_sec_ant"])

        if "obdh_mem_sec_edc" in data:
            self.label_obdh_mem_sec_edc.set_text(data["obdh_mem_sec_edc"])

        if "obdh_mem_sec_plx" in data:
            self.label_obdh_mem_sec_payloadx.set_text(data["obdh_mem_sec_plx"])

        if "obdh_mem_sec_sbcd" in data:
            self.label_obdh_mem_sec_sbcd.set_text(data["obdh_mem_sec_sbcd"])

        if "obdh_pos_lat" in data:
            self.label_obdh_position_lattitude.set_text(data["obdh_pos_lat"] + "°")

        if "obdh_pos_lon" in data:
            self.label_obdh_position_longitude.set_text(data["obdh_pos_lon"] + "°")

        if "obdh_pos_alt" in data:
            self.label_obdh_position_altitude.set_text(data["obdh_pos_alt"] + " " + "km")

        if "obdh_pos_ts" in data:
            self.label_obdh_position_date.set_text(datetime.datetime.fromtimestamp(int(data["obdh_pos_ts"])).strftime('%Y/%m/%d'))
            self.label_obdh_position_time.set_text(datetime.datetime.fromtimestamp(int(data["obdh_pos_ts"])).strftime('%H:%M:%S'))

        if "obdh_pos_tle_line_1" in data:
            self.textbuffer_obdh_position_tle.set_text(data["obdh_pos_tle_line_1"])

        if "obdh_pos_tle_line_2" in data:
            self.textbuffer_obdh_position_tle.set_text(data["obdh_pos_tle_line_2"])

        if "obdh_pos_last_tle_upd_ts" in data:
            self.label_obdh_position_date.set_text(datetime.datetime.fromtimestamp(int(data["obdh_pos_last_tle_upd_ts"])).strftime('%Y/%m/%d'))
            self.label_obdh_position_time.set_text(datetime.datetime.fromtimestamp(int(data["obdh_pos_last_tle_upd_ts"])).strftime('%H:%M:%S'))

        if "obdh_op_last_val_tc" in data:
            self.label_obdh_op_last_valid_tc.set_text(data["obdh_op_last_val_tc"])

        if "obdh_op_mode" in data:
            if int(data["obdh_op_mode"]) == 0:
                self.label_obdh_op_mode.set_text("Normal")
            elif int(data["obdh_op_mode"]) == 1:
                self.label_obdh_op_mode.set_text("Hibernation")
            elif int(data["obdh_op_mode"]) == 2:
                self.label_obdh_op_mode.set_text("Standby")
            else:
                self.label_obdh_op_mode.set_text("Unknown")

        if "obdh_op_last_mode_change_ts" in data:
            self.label_obdh_op_date_last_mode_change.set_text(datetime.datetime.fromtimestamp(int(data["obdh_op_last_mode_change_ts"])).strftime('%Y/%m/%d'))
            self.label_obdh_op_time_last_mode_change.set_text(datetime.datetime.fromtimestamp(int(data["obdh_op_last_mode_change_ts"])).strftime('%H:%M:%S'))

        if "obdh_op_mode_dur" in data:
            self.label_obdh_op_mode_duration.set_text(data["obdh_op_mode_dur"] + " " + "sec")

        if "obdh_op_init_hib" in data:
            if int(data["obdh_op_init_hib"]) == 0:
                self.label_obdh_op_initial_hib.set_text("Not Executed")
            if int(data["obdh_op_init_hib"]) == 1:
                self.label_obdh_op_initial_hib.set_text("Executed")
            else:
                self.label_obdh_op_initial_hib.set_text("Unknown")

        if "obdh_op_init_hib_time" in data:
            self.label_obdh_op_initial_hib_time.set_text(data["obdh_op_init_hib_time"] + " " + "min")

        if "obdh_op_manual_mode" in data:
            if int(data["obdh_op_manual_mode"]) == 0:
                self.label_obdh_op_manual_mode.set_text("Disabled")
            elif int(data["obdh_op_manual_mode"]) == 1:
                self.label_obdh_op_manual_mode.set_text("Enabled")
            else:
                self.label_obdh_op_manual_mode.set_text("Unknown")

        if "obdh_op_main_edc" in data:
            if int(data["obdh_op_main_edc"]) == 1:
                self.label_obdh_op_main_edc.set_text("Main")
            elif int(data["obdh_op_main_edc"]) == 2:
                self.label_obdh_op_main_edc.set_text("Redundant")
            else:
                self.label_obdh_op_main_edc.set_text("Unknown")

        if "obdh_op_general_tm" in data:
            if int(data["obdh_op_general_tm"]) == 0:
                self.label_obdh_op_general_tm.set_text("Disabled")
            elif int(data["obdh_op_general_tm"]) == 1:
                self.label_obdh_op_general_tm.set_text("Enabled")
            else:
                self.label_obdh_op_general_tm.set_text("Unknown")

        if "obdh_op_pl_main_state" in data:
            if int(data["obdh_op_pl_main_state"]) == 0:
                self.label_obdh_op_main_pl_state.set_text("Disabled")
            else:
                self.label_obdh_op_main_pl_state.set_text(data["obdh_op_main_pl_state"])

        if "obdh_op_pl_sec_state" in data:
            if int(data["obdh_op_pl_sec_state"]) == 0:
                self.label_obdh_op_secondary_pl_state.set_text("Disabled")
            else:
                self.label_obdh_op_secondary_pl_state.set_text(data["obdh_op_sec_pl_state"])

        if "obdh_op_last_reading_ts" in data:
            self.label_obdh_op_date_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_op_last_reading_ts"])).strftime('%Y/%m/%d'))
            self.label_obdh_op_date_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_op_last_reading_ts"])).strftime('%H:%M:%S'))

        if "obdh_op_remaining_hib_time" in data:
            self.label_obdh_op_remaining_hib_time.set_text(data["obdh_op_remaining_hib_time"] + " " + "min")

        if "obdh_last_valid_tc_rssi" in data:
            self.label_obdh_op_date_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_last_valid_tc_rssi"])).strftime('%Y/%m/%d'))
            self.label_obdh_op_time_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_last_valid_tc_rssi"])).strftime('%H:%M:%S'))

        if "obdh_sensor_read_ts" in data:
            self.label_obdh_op_date_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_sensor_read_ts"])).strftime('%Y/%m/%d'))
            self.label_obdh_op_time_last_reading.set_text(datetime.datetime.fromtimestamp(int(data["obdh_sensor_read_ts"])).strftime('%H:%M:%S'))

        if "ttc_radio1_temp" in data:
            self.label_ttc_radio2_temp.set_text(str((int(data["ttc_radio1_temp"]) - 273)) + " " + "°C")

        if "ant_temp" in data:
            self.label_ant_temp.set_text(str((int(data["ant_temp"]) - 273)) + " " + "°C")

        if "ant_status" in data:
            ant_stat = int(data["ant_status"])
            ant_mp1_deployed    = (ant_stat >> 15) & 0x0001
            ant_mp1_dep_stop    = (ant_stat >> 14) & 0x0001
            ant_mp1_dep_sys     = (ant_stat >> 13) & 0x0001
            ant_mp2_deployed    = (ant_stat >> 11) & 0x0001
            ant_mp2_dep_stop    = (ant_stat >> 10) & 0x0001
            ant_mp2_dep_sys     = (ant_stat >> 9) & 0x0001
            ant_mp3_deployed    = (ant_stat >> 7) & 0x0001
            ant_mp3_dep_stop    = (ant_stat >> 6) & 0x0001
            ant_mp3_dep_sys     = (ant_stat >> 5) & 0x0001
            ant_mp4_deployed    = (ant_stat >> 3) & 0x0001
            ant_mp4_dep_stop    = (ant_stat >> 2) & 0x0001
            ant_mp4_dep_sys     = (ant_stat >> 1) & 0x0001
            ant_ignore_sw       = (ant_stat >> 8) & 0x0001
            ant_indb            = (ant_stat >> 4) & 0x0001
            ant_armed           = ant_stat & 0x0001

            if ant_indb:
                self.label_ant_indep_burn.set_text("Enabled")
            else:
                self.label_ant_indep_burn.set_text("Disabled")

            if ant_ignore_sw:
                self.label_ant_ignore_switches.set_text("True")
            else:
                self.label_ant_ignore_switches.set_text("False")

            if ant_armed:
                self.label_ant_armed.set_text("True")
            else:
                self.label_ant_armed.set_text("False")

            if ant_mp1_deployed:
                self.label_ant_mp1_deployed.set_text("True")
            else:
                self.label_ant_mp1_deployed.set_text("False")

            if ant_mp1_dep_stop:
                self.label_ant_mp1_dep_stop.set_text("Timeout")
            else:
                self.label_ant_mp1_dep_stop.set_text("Other")

            if ant_mp1_dep_sys:
                self.label_ant_mp1_dep_sys.set_text("Activated")

            else:
                self.label_ant_mp1_dep_sys.set_text("Deactivated")

            if ant_mp2_deployed:
                self.label_ant_mp2_deployed.set_text("True")
            else:
                self.label_ant_mp2_deployed.set_text("False")

            if ant_mp2_dep_stop:
                self.label_ant_mp2_dep_stop.set_text("Timeout")
            else:
                self.label_ant_mp2_dep_stop.set_text("Other")

            if ant_mp2_dep_sys:
                self.label_ant_mp2_dep_sys.set_text("Activated")
            else:
                self.label_ant_mp2_dep_sys.set_text("Deactivated")

            if ant_mp3_deployed:
                self.label_ant_mp3_deployed.set_text("True")
            else:
                self.label_ant_mp3_deployed.set_text("False")

            if ant_mp3_dep_stop:
                self.label_ant_mp3_dep_stop.set_text("Timeout")
            else:
                self.label_ant_mp3_dep_stop.set_text("Other")

            if ant_mp3_dep_sys:
                self.label_ant_mp3_dep_sys.set_text("Activated")
            else:
                self.label_ant_mp3_dep_sys.set_text("Deactivated")

            if ant_mp4_deployed:
                self.label_ant_mp4_deployed.set_text("True")
            else:
                self.label_ant_mp4_deployed.set_text("False")

            if ant_mp4_dep_stop:
                self.label_ant_mp4_dep_stop.set_text("Timeout")
            else:
                self.label_ant_mp4_dep_stop.set_text("Other")

            if ant_mp4_dep_sys:
                self.label_ant_mp4_dep_sys.set_text("Activated")
            else:
                self.label_ant_mp4_dep_sys.set_text("Deactivated")

        if "edc1_ts" in data:
            self.label_edc1_date.set_text(datetime.datetime.fromtimestamp(int(data["edc1_ts"])).strftime('%Y/%m/%d'))
            self.label_edc1_time.set_text(datetime.datetime.fromtimestamp(int(data["edc1_ts"])).strftime('%H:%M:%S'))

        if "edc1_elapsed_tm" in data:
            self.label_edc1_elapsed_time.set_text(data["edc1_elapsed_tm"] + " " + "sec")

        if "edc1_volt" in data:
            self.label_edc1_volt.set_text(data["edc1_volt"] + " " + "mV")

        if "edc1_curr_dig" in data:
            self.label_edc1_curr_dig.set_text(data["edc1_curr_dig"] + " " + "mA")

        if "edc1_curr_ana" in data:
            self.label_edc1_curr_ana.set_text(data["edc1_curr_ana"] + " " + "mA")

        if "edc1_temp" in data:
            self.label_edc1_temp.set_text(data["edc1_temp"] + " " + "°C")

        if "edc1_pll_sync" in data:
            if int(data["edc1_pll_sync"] == 0):
                self.label_edc1_pll_sync.set_text("Disabled")
            elif int(data["edc1_pll_sync"] == 0):
                self.label_edc1_pll_sync.set_text("Enabled")
            else:
                self.label_edc1_pll_sync.set_text("Unknown")

        if "edc1_adc_rms_lvl" in data:
            self.label_edc1_adc_rms_lvl.set_text(data["edc1_adc_rms_lvl"])

        if "edc1_tot_ptt_pkg" in data:
            self.label_edc1_tot_ptt_pkg.set_text(data["edc1_tot_ptt_pkg"])

        if "edc1_ptt_dec_ch" in data:
            self.label_edc1_ptt_dec_ch.set_text(data["edc1_ptt_dec_ch"])

        if "edc1_mss_err_count" in data:
            self.label_edc1_mss_err_count.set_text(data["edc1_mss_err_count"])

        if "edc2_ts" in data:
            self.label_edc1_date.set_text(datetime.datetime.fromtimestamp(int(data["edc2_ts"])).strftime('%Y/%m/%d'))
            self.label_edc1_time.set_text(datetime.datetime.fromtimestamp(int(data["edc2_ts"])).strftime('%H:%M:%S'))

        if "edc2_elapsed_tm" in data:
            self.label_edc1_elapsed_time.set_text(data["edc2_elapsed_tm"] + " " + "sec")

        if "edc2_volt" in data:
            self.label_edc1_volt.set_text(data["edc2_volt"] + " " + "mV")

        if "edc2_curr_dig" in data:
            self.label_edc1_curr_dig.set_text(data["edc2_curr_dig"] + " " + "mA")

        if "edc2_curr_ana" in data:
            self.label_edc1_curr_ana.set_text(data["edc2_curr_ana"] + " " + "mA")

        if "edc2_temp" in data:
            self.label_edc1_temp.set_text(data["edc2_temp"] + " " + "°C")

        if "edc2_pll_sync" in data:
            if int(data["edc2_pll_sync"] == 0):
                self.label_edc1_pll_sync.set_text("Disabled")
            elif int(data["edc2_pll_sync"] == 0):
                self.label_edc1_pll_sync.set_text("Enabled")
            else:
                self.label_edc1_pll_sync.set_text("Unknown")

        if "edc2_adc_rms_lvl" in data:
            self.label_edc1_adc_rms_lvl.set_text(data["edc2_adc_rms_lvl"])

        if "edc2_tot_ptt_pkg" in data:
            self.label_edc1_tot_ptt_pkg.set_text(data["edc2_tot_ptt_pkg"])

        if "edc2_ptt_dec_ch" in data:
            self.label_edc1_ptt_dec_ch.set_text(data["edc2_ptt_dec_ch"])

        if "edc2_mss_err_count" in data:
            self.label_edc1_mss_err_count.set_text(data["edc2_mss_err_count"])

    def _load_default_values_eps(self):
        self.label_eps_mcu_date.set_text("1970/01/01")
        self.label_eps_mcu_time.set_text("00:00:00")
        self.label_eps_mcu_temp.set_text("0 °C")
        self.label_eps_mcu_curr.set_text("0 mA")
        self.label_eps_mcu_last_reset_cause.set_text("0")
        self.label_eps_mcu_reset_count.set_text("0")
        self.label_eps_sp_volt_mypx.set_text("0 mV")
        self.label_eps_sp_volt_mxpz.set_text("0 mV")
        self.label_eps_sp_volt_mzpy.set_text("0 mV")
        self.label_eps_sp_curr_mx.set_text("0 mA")
        self.label_eps_sp_curr_px.set_text("0 mA")
        self.label_eps_sp_curr_my.set_text("0 mA")
        self.label_eps_sp_curr_py.set_text("0 mA")
        self.label_eps_sp_curr_mz.set_text("0 mA")
        self.label_eps_sp_curr_pz.set_text("0 mA")
        self.label_eps_mppt_dc_ch_1.set_text("0 %")
        self.label_eps_mppt_dc_ch_2.set_text("0 %")
        self.label_eps_mppt_dc_ch_3.set_text("0 %")
        self.label_eps_mppt_mode_ch_1.set_text("Automatic")
        self.label_eps_mppt_mode_ch_2.set_text("Automatic")
        self.label_eps_mppt_mode_ch_3.set_text("Automatic")
        self.label_eps_mppt_output_volt.set_text("0 mV")
        self.label_eps_rtd_ch_0.set_text("0 °C")
        self.label_eps_rtd_ch_1.set_text("0 °C")
        self.label_eps_rtd_ch_2.set_text("0 °C")
        self.label_eps_rtd_ch_3.set_text("0 °C")
        self.label_eps_rtd_ch_4.set_text("0 °C")
        self.label_eps_rtd_ch_5.set_text("0 °C")
        self.label_eps_rtd_ch_6.set_text("0 °C")
        self.label_eps_bat_volt.set_text("0 mV")
        self.label_eps_bat_curr.set_text("0 mA")
        self.label_eps_bat_average_curr.set_text("0 mA")
        self.label_eps_bat_acc_curr.set_text("0 mA")
        self.label_eps_bat_charge.set_text("0 mAh")
        self.label_eps_bat_heater_1_dc.set_text("0 %")
        self.label_eps_bat_heater_2_dc.set_text("0 %")
        self.label_eps_bat_heater_1_mode.set_text("Automatic")
        self.label_eps_bat_heater_2_mode.set_text("Automatic")
        self.label_eps_bat_temp_monitor.set_text("0 °C")
        self.label_eps_bat_status.set_text("-")
        self.label_eps_bat_protection.set_text("-")
        self.label_eps_bat_cycle_counter.set_text("0")
        self.label_eps_bat_raac.set_text("0 mAh")
        self.label_eps_bat_rsac.set_text("0 mAh")
        self.label_eps_bat_rarc.set_text("0 %")
        self.label_eps_bat_rsrc.set_text("0 %")

    def _load_default_values_obdh(self):
        self.label_obdh_mcu_date.set_text("1970/01/01")
        self.label_obdh_mcu_time.set_text("00:00:00")
        self.label_obdh_mcu_temp.set_text("0 °C")
        self.label_obdh_mcu_last_reset_cause.set_text("0")
        self.label_obdh_mcu_reset_count.set_text("0")
        self.label_obdh_general_voltage.set_text("0 mV")
        self.label_obdh_general_current.set_text("0 mA")
        self.label_obdh_mem_sec_obdh.set_text("0")
        self.label_obdh_mem_sec_eps.set_text("0")
        self.label_obdh_mem_sec_ttc_0.set_text("0")
        self.label_obdh_mem_sec_ttc_1.set_text("0")
        self.label_obdh_mem_sec_antenna.set_text("0")
        self.label_obdh_mem_sec_edc.set_text("0")
        self.label_obdh_mem_sec_payloadx.set_text("0")
        self.label_obdh_mem_sec_sbcd.set_text("0")
        self.label_obdh_position_lattitude.set_text("0°")
        self.label_obdh_position_longitude.set_text("0°")
        self.label_obdh_position_altitude.set_text("0 km")
        self.label_obdh_position_date.set_text("1970/01/01")
        self.label_obdh_position_time.set_text("00:00:00")
        self.textbuffer_obdh_position_tle.set_text(
                "25544U 98067A   25054.44635474  .00024560  00000+0  44723-3 0  9992\n" +
                "25544  51.6356 150.3745 0005991 304.7544  55.2880 15.49325184497521")
        self.label_obdh_position_date.set_text("1970/01/01")
        self.label_obdh_position_time.set_text("00:00:00")
        self.label_obdh_op_last_valid_tc.set_text("0")
        self.label_obdh_op_mode.set_text("Normal")
        self.label_obdh_op_date_last_mode_change.set_text("1970/01/01")
        self.label_obdh_op_time_last_mode_change.set_text("00:00:00")
        self.label_obdh_op_mode_duration.set_text("0 sec")
        self.label_obdh_op_initial_hib.set_text("Not Executed")
        self.label_obdh_op_initial_hib_time.set_text("0 min")
        self.label_obdh_op_manual_mode.set_text("Enabled")
        self.label_obdh_op_main_edc.set_text("0")
        self.label_obdh_op_general_tm.set_text("Enabled")
        self.label_obdh_op_main_pl_state.set_text("0")
        self.label_obdh_op_secondary_pl_state.set_text("0")
        self.label_obdh_op_date_last_reading.set_text("1970/01/01")
        self.label_obdh_op_time_last_reading.set_text("00:00:00")
        self.label_obdh_op_remaining_hib_time.set_text("0 sec")

    def _create_socket_server(self, adr, port):
        """Create a TCP/IP socket server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((adr, port))
            server_socket.listen(1)
            return server_socket
        except socket.error as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error creating a socket server!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
            return None

    def _handle_new_connection(self, source, condition):
        """Handle incoming connections"""
        if condition == GLib.IO_IN:
            client_socket, address = self._server_socket.accept()

            # Create an IOChannel for the client socket to handle incoming data
            client_io_channel = GLib.IOChannel(client_socket.fileno())
            client_io_channel.set_encoding(None)  # Binary mode (important for raw data)

            # Monitor the client socket for incoming data
            GLib.io_add_watch(client_io_channel, GLib.IO_IN, self._handle_data, client_socket)

        return True  # Keep the handler active

    def _handle_data(self, source, condition, client_socket):
        """Handle incoming data from the client"""
        if condition == GLib.IO_IN:
            try:
                data = client_socket.recv(2048)  # Read incoming data (max 1024 bytes)
                if data:
                    self._decode_pkt(data)
                else:
                    # Connection closed by client
                    client_socket.close()
                    return False  # Stop the IO watch for this client
            except socket.error as e:
                client_socket.close()
                return False  # Stop the IO watch for this client
        return True  # Keep the handler active
