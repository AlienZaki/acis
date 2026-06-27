# Keep kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class **$$serializer { *; }
-keepclassmembers @kotlinx.serialization.Serializable class ** { *** Companion; }
-keepclassmembers enum * { public static **[] values(); public static ** valueOf(java.lang.String); }

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
