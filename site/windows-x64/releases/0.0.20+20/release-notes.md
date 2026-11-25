Released on November 16, 2026.

* **PERF**: Avoided rebuilding layer controls on pixel edits.
* **PERF**: Bound preparation work and resource collection memory.
* **PERF**: Bounded download buffers while preserving throughput.
* **PERF**: Bounded vector thumbnails and shared histogram caching.
* **PERF**: Further reduced subject segmentation memory peaks.
* **PERF**: Improved live paint performance.
* **PERF**: Improved vector documents spaning & zooming speed.
* **PERF**: Moved native vector JSON work off the UI thread.
* **PERF**: Reduced selection inspection and geometry work.
* **PERF**: Retained bounded vector proof and comparison preparation.
* **PERF**: Scoped document updates and isolated layer hover feedback.
* **PERF**: Shared lazy geometry across vector editor consumers.
* **PERF**: Shared lazy timelines between image and vector editors.
* **PERF**: Shared retained vector projections across inspection tasks.
* **FEAT**: Added AI noise reduction and super resolution.
* **FEAT**: Added an AI method to Content-Aware Fill powered by LaMa.
* **FEAT**: Added native text-path geometry, predefined paragraph lists and Adobe variable-font instance names.
* **FEAT**: Added on-device Select Subject and Remove Background with downloadable models.
* **FEAT**: Added paint symmetry to the brush, pencil and eraser.
* **FEAT**: Added shared progress, cancellation and partial results.
* **FEAT**: Added sky replacement and kept the canvas painted while a prepared composite starts.
* **FEAT**: Added support for APNG and animated WebPs.
* **FEAT**: Added texture, clarity, dehaze, color grading and grain to Camera Raw.
* **FEAT**: Added the Object selection tool powered by SAM 2.1.
* **FEAT**: Added the ability to have a checkerboard background for vector documents.
* **FEAT**: Added the blob brush and the perspective grid.
* **FEAT**: Added tips about the vector editor and other features.
* **FEAT**: Enabled web as a target platform.
* **FEAT**: Implemented replayable vector library actions.
* **FEAT**: Improved gradients and texts handling.
* **FEAT**: Improved live paint.
* **FEAT**: Kept native precision and colour space in AI noise reduction and super resolution.
* **FEAT**: Kept native precision and colour space in the AI Content-Aware Fill.
* **FEAT**: Moved the built-in skies to an asset, accepted gradient files and removed the halo around branches in sky replacement.
* **FEAT**: Now displaying ONNX in the app settings.
* **FEAT**: Now displaying local models size in the app settings.
* **FEAT**: Opened CIELab and ICCLab TIFF files as Lab documents.
* **FEAT**: Opened the AI tools to CMYK, Lab and grayscale documents.
* **FEAT**: Shared destinations and repeat exports across editors.
* **FEAT**: Shared file drops, color sampling and keyboard pane navigation.
* **FEAT**: Shared reversible blend previews across editors.
* **FEAT**: Shared shortcut aliases and temporary vector tools.
* **FEAT**: Unified persistence and history feedback.
* **FIX**: Added grain during the 16-bit conversion and processed presence, grading and grain row by row.
* **FIX**: Adjusted macOS spacing for rounded window corners.
* **FIX**: Aligned Sentry pins and reviewed native recipes.
* **FIX**: Asked once before replacing a destination in both editors.
* **FIX**: Bound shared navigator controls to their own views.
* **FIX**: Bound text panels and dimensions to their documents.
* **FIX**: Bound vector readouts and sampling to their owning views.
* **FIX**: Classified protected placements and forwarded canvas wheel input.
* **FIX**: Completed view input lifecycles and shared display controls.
* **FIX**: Corrected Wayland offsets and large soft brush gradients.
* **FIX**: Corrected content-aware sampling and colour adaptation.
* **FIX**: Corrected sky replacement and made bright halo reduction optional.
* **FIX**: Finalized shared shortcut and preview lifecycles.
* **FIX**: Fixed regressions from the paste, blend preview and proof review.
* **FIX**: Fixed regressions from the persistence and shortcut review.
* **FIX**: Fixed regressions from the progress and preview review.
* **FIX**: Fixed regressions from the scoped barriers, gradient and inspection review.
* **FIX**: Fixed regressions from the shared input and export review.
* **FIX**: Fixed stale paint command availability and shared warp overlay painting from the application review.
* **FIX**: Fixed stale segmentation results and bounded model sessions.
* **FIX**: Harmonized recent editor surfaces and bounded Camera Raw mask inputs.
* **FIX**: Harmonized selector focus and adopted ForUI menu semantics.
* **FIX**: Kept proofing and display modes independent per view.
* **FIX**: Kept search and spelling bound to their document lifetime.
* **FIX**: Open encrypted documents and unify canvas scrolling.
* **FIX**: Precache only the current worker and runtime versions.
* **FIX**: Preserved coherent saves, exports and preview targets.
* **FIX**: Preserved result placement and cancelled superseded selections.
* **FIX**: Preserved translucent pixels and stabilized browser validation.
* **FIX**: Reduced subject segmentation memory peaks.
* **FIX**: Repaired macOS inference and now downloading notarized runtimes on demand.
* **FIX**: Restore locked setup in a fresh checkout.
* **FIX**: Restored page loading and visible canvas scrolling.
* **FIX**: Retained bounded previews with each frame's resources.
* **FIX**: Scoped operation barriers and command admission to documents.
* **FIX**: Serialized document pastes with shared activity feedback.
* **FIX**: Shared complete wheel and trackpad navigation.
* **FIX**: Shared playback visibility across editor presentations.
* **FIX**: Various UI fixes and improvements.
* **FIX**: Various fixes and improvements.
* **CHORE**: Cleaned analyzer hints in shared editor regressions.
* **CHORE**: Integrate concurrent browser fixes and validation guidance.
* **CHORE**: Removed redundant blend preview import.
* **CHORE**: Shared more mechanisms between the raster and the vector editors.
* **CHORE**: Various fixes and improvements.
* **REFACTOR**: Retained gradient and composition state per document.
* **REFACTOR**: Separated resource services and streamlined clipboard encoding.
* **REFACTOR**: Shared comparison hosting and originating view scope.
* **REFACTOR**: Shared window placement between photo and vector documents in the view registry.
* **REFACTOR**: Unified the photo and vector view registries and viewport controllers.
