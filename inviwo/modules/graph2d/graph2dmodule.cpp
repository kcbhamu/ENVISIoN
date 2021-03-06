/*********************************************************************************
 *
 * Copyright (c) 2017 Robert Cranston
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************************/
 /*
  *   Alterations to this file by Abdullatif Ismail
  *
  *   To the extent possible under law, the person who associated CC0
  *   with the alterations to this file has waived all copyright and
  *   related or neighboring rights to the alterations made to this file.
  *
  *   You should have received a copy of the CC0 legalcode along with
  *   this work.  If not, see
  *   <http://creativecommons.org/publicdomain/zero/1.0/>.
  */

#include <modules/graph2d/graph2dmodule.h>

#include <modules/graph2d/datastructures/graph2ddata.h>
#include <modules/graph2d/processors/dataframecollector.h>
#include <modules/graph2d/processors/hdf5pathselectionint.h>
#include <modules/graph2d/processors/hdf5pathselectionintvector.h>
#include <modules/graph2d/processors/hdf5pathselectionallchildren.h>
#include <modules/graph2d/processors/hdf5topoint.h>
#include <modules/graph2d/processors/hdf5tofunction.h>
#include <modules/graph2d/processors/functionoperationunary.h>
#include <modules/graph2d/processors/functionoperationnary.h>
#include <modules/graph2d/processors/functiontodataframe.h>
#include <modules/graph2d/processors/lineplotprocessor.h>

namespace inviwo {

graph2dModule::graph2dModule(InviwoApplication* app) : InviwoModule(app, "graph2d") {

    // Processors.
    registerProcessor<DataFrameCollector>();
    registerProcessor<HDF5PathSelectionInt>();
    registerProcessor<HDF5PathSelectionIntVector>();
    registerProcessor<HDF5PathSelectionAllChildren>();
    registerProcessor<HDF5ToPoint>();
    registerProcessor<HDF5ToFunction>();
    registerProcessor<FunctionOperationUnary>();
    registerProcessor<FunctionOperationNary>();
    registerProcessor<FunctionToDataFrame>();
    registerProcessor<LinePlotProcessor>();

    // Ports.
    registerPort<DataOutport<Point>>();
    registerPort<DataInport<Point>>();
    registerPort<DataOutport<Function>>();
    registerPort<DataInport<Function>>();
}

} // namespace
