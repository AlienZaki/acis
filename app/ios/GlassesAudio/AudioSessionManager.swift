/**
 * AudioSessionManager — native iOS module to switch AVAudioSession to .playback
 * category so TTS output routes via A2DP to the Meta Ray-Ban glasses.
 *
 * Register in AppDelegate.m / AppDelegate.mm:
 *   // nothing needed — RCTBridgeModule auto-registers
 *
 * Bluetooth A2DP / HFP mutual-exclusion note:
 *   When the glasses mic is active via HFP, iOS already uses a .playAndRecord
 *   session on the SCO link (full-duplex, 8 kHz mono).  This method is called
 *   when mic source == "phone" so we can use .playback + A2DP (44.1 kHz stereo).
 *   Do not call activateA2DPSession while a glasses mic HFP session is running —
 *   that would drop the mic stream.
 */

import Foundation
import AVFoundation
import React

@objc(AudioSessionManager)
class AudioSessionManager: NSObject, RCTBridgeModule {

  static func moduleName() -> String! { "AudioSessionManager" }
  static func requiresMainQueueSetup() -> Bool { false }

  @objc func activateA2DPSession(
    _ resolve: @escaping RCTPromiseResolveBlock,
    rejecter reject: @escaping RCTPromiseRejectBlock
  ) {
    do {
      let session = AVAudioSession.sharedInstance()
      try session.setCategory(.playback, mode: .default, options: [])
      try session.setActive(true, options: .notifyOthersOnDeactivation)
      resolve(nil)
    } catch {
      reject("AVAudioSession", error.localizedDescription, error)
    }
  }

  /// Returns true if an A2DP output (glasses) is the current route.
  @objc func isA2DPActive(
    _ resolve: @escaping RCTPromiseResolveBlock,
    rejecter reject: @escaping RCTPromiseRejectBlock
  ) {
    let hasA2DP = AVAudioSession.sharedInstance().currentRoute.outputs.contains {
      $0.portType == .bluetoothA2DP
    }
    resolve(hasA2DP)
  }
}
