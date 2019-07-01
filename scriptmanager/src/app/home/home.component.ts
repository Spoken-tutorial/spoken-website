import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss;
  public tutorials;
  public langId: number;
  public fossId: number;
  public index: number;
  public description: boolean = false;
  public langData: any;

  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService
  ) { }

  public getLanguage(langIndex) {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.index = langIndex
        localStorage.setItem('fossIndex', String(this.index))

        this.fossId = res[langIndex].foss_category.id
        localStorage.setItem('fossId', String(this.fossId))

        this.langData = res[langIndex]['language']
        this.description = true
      }
    );
  }

  public fetchFossTutorials(languageId) {
    this.langId = languageId
    localStorage.setItem('langId', String(this.langId))

    let local_fossId = localStorage.getItem("fossId");
    let local_langId = localStorage.getItem("langId");

    this.tutorialService.getFossTutorials(local_fossId, local_langId).subscribe(
      (res) => {
        this.tutorials = res
      },
      (err) => {
        console.log('Failed to fetch tutorial categories');
        console.error(err);
      }
    );
  }

  public fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.foss = res
      },
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  ngOnInit() {
    this.langData = { id: -1, name: "" };
    this.fetchAllFoss();

    let local_fossIndex = localStorage.getItem("fossIndex");
    let local_langId = localStorage.getItem("langId");

    if (localStorage.length > 1) {
      this.getLanguage(local_fossIndex)
      this.fetchFossTutorials(local_langId)
    }
  };

}
